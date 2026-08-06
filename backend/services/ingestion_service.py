import re
from collections import Counter

from ingestion_pipeline.parser import parse_pdf
from ingestion_pipeline.text_splitter import split_text
from database.vector_store import store_chunks, find_similar_with_scores

from backend.state.document_store import set_current_document


def extract_case_citations(text: str):
    """
    Extract legal case citations from text.
    Pattern matches: SomeName v. SomeName
    """

    # FIX: Tightened pattern to avoid over-matching partial words
    pattern = r"\b[A-Z][a-zA-Z\s]{1,40} v\. [A-Z][a-zA-Z\s]{1,40}\b"

    cases = re.findall(pattern, text)

    # Strip extra whitespace from each match
    cases = [c.strip() for c in cases]

    return list(set(cases))


def process_pdf(file, thread_id="default"):
    """
    Process uploaded judgement PDF.
    Supports both Streamlit and FastAPI uploads.
    """

    # Detect filename + bytes
    if hasattr(file, "filename"):  # FastAPI
        filename = file.filename
        pdf_bytes = file.file.read()

    else:  # Streamlit
        filename = file.name
        pdf_bytes = file.read()

    # FIX: Guard against parse failure
    try:
        text = parse_pdf(pdf_bytes)
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF '{filename}': {e}")

    # FIX: Guard against empty parsed text
    if not text or not text.strip():
        raise ValueError(f"PDF '{filename}' appears to be empty or unreadable (scanned image?). "
                         "Please upload a text-based PDF.")

    # Store document for tools
    set_current_document(text, thread_id)

    # Extract citations
    citations = extract_case_citations(text)

    # Split into chunks
    chunks = split_text(text)

    # FIX: Guard against empty chunks
    if not chunks:
        raise ValueError(f"No chunks were generated from '{filename}'. Check the text splitter config.")

    # FIX: Guard against store failure
    try:
        store_chunks(chunks, filename)
    except Exception as e:
        raise RuntimeError(f"Failed to store chunks for '{filename}': {e}")

    print(f"Chunks stored: {len(chunks)}")

    # --- Build visual insights data ---

    # IPC section frequency (bar chart data)
    ipc_pattern = r"Section\s(\d+[A-Z]?)"
    ipc_matches = re.findall(ipc_pattern, text)
    ipc_counts = Counter(ipc_matches)
    sections_data = [{"section": f"Sec {s}", "count": c}
                     for s, c in ipc_counts.most_common(15)]

    # Precedent citation frequency (bar chart data)
    citation_counts = Counter(citations)
    precedents_data = [{"name": name.strip()[:40], "count": c}
                       for name, c in citation_counts.most_common(10)]

    # Outcome pattern keywords (pie chart data)
    text_lower = text.lower()
    outcome_keywords = {
        "Convicted": len(re.findall(r"\bconvict(?:ed|ion)\b", text_lower)),
        "Acquitted": len(re.findall(r"\bacquitt(?:ed|al)\b", text_lower)),
        "Dismissed": len(re.findall(r"\bdismiss(?:ed|al)\b", text_lower)),
        "Allowed": len(re.findall(r"\ballowed\b", text_lower)),
        "Upheld": len(re.findall(r"\bupheld\b", text_lower)),
        "Remanded": len(re.findall(r"\bremand(?:ed)?\b", text_lower)),
    }
    outcomes_data = [{"name": k, "value": v}
                     for k, v in outcome_keywords.items() if v > 0]

    # Similar cases with scores (table data)
    summary_text = text[:500]
    similar_cases = []
    try:
        similar_cases = find_similar_with_scores(summary_text, n_results=5)
    except Exception:
        pass

    # --- Extract structured case metadata ---
    case_meta = _extract_case_metadata(text, citations, ipc_matches, outcomes_data)

    return {
        "filename": filename,
        "chunks_created": len(chunks),
        "citations_found": citations,
        "insights": {
            "sections": sections_data,
            "precedents": precedents_data,
            "outcomes": outcomes_data,
            "similar_cases": similar_cases,
            "case_meta": case_meta,
        }
    }


def _extract_case_metadata(text, citations, ipc_matches, outcomes_data):
    """Extract structured metadata fields from legal text."""
    text_lower = text.lower()
    first_2k = text[:2000]

    # Case title — look for "X v. Y" or "X vs Y" near the top
    case_title = ""
    title_match = re.search(
        r"([A-Z][A-Za-z\s\.]+?)\s+(?:v\.|vs\.?)\s+([A-Z][A-Za-z\s\.]+)",
        first_2k
    )
    if title_match:
        case_title = title_match.group(0).strip()[:80]

    # Court type
    court = ""
    court_patterns = [
        (r"Supreme Court of India", "Supreme Court of India"),
        (r"High Court of ([A-Za-z\s]+)", None),
        (r"District Court", "District Court"),
        (r"Sessions Court", "Sessions Court"),
        (r"Tribunal", "Tribunal"),
    ]
    for pat, label in court_patterns:
        m = re.search(pat, first_2k, re.IGNORECASE)
        if m:
            court = label if label else f"High Court of {m.group(1).strip()}"
            break

    # Year
    year = ""
    year_match = re.search(r"\b(19|20)\d{2}\b", first_2k)
    if year_match:
        year = year_match.group(0)

    # Verdict — determine from outcome keywords
    verdict = "Not determined"
    if outcomes_data:
        top = max(outcomes_data, key=lambda x: x["value"])
        verdict = top["name"]

    # Case number / appeal number
    case_number = ""
    cn_match = re.search(
        r"(?:Criminal|Civil|Writ|SLP|Appeal|Case|Petition|Reference)\s*(?:No\.?|Number)\s*[\d/\-\(\)of\s]+",
        first_2k, re.IGNORECASE
    )
    if cn_match:
        case_number = cn_match.group(0).strip()[:60]

    # Petitioner and Respondent
    petitioner = ""
    respondent = ""
    if title_match:
        petitioner = title_match.group(1).strip()[:50]
        respondent = title_match.group(2).strip()[:50]

    # Issues — look for "issue" or "question" keywords
    issues = []
    issue_patterns = [
        r"(?:issue|question)\s*(?:is|was|for consideration|that arises)[:\s]*([^\n\.]{10,120})",
        r"(?:whether)\s+([^\n\.]{10,120})",
    ]
    for pat in issue_patterns:
        for m in re.finditer(pat, text_lower):
            issue_text = m.group(1).strip().capitalize()
            if len(issue_text) > 15:
                issues.append(issue_text[:120])
            if len(issues) >= 3:
                break
        if issues:
            break

    # Petitioner arguments
    pet_args = _extract_arguments(text, ["petitioner", "appellant", "complainant", "prosecution"])

    # Respondent arguments
    resp_args = _extract_arguments(text, ["respondent", "defendant", "accused", "defence"])

    # Sections cited (unique, sorted)
    sections_cited = sorted(set(f"Section {s}" for s in ipc_matches))[:12]

    # Summary — clean first meaningful paragraph
    summary = _extract_clean_summary(text)

    return {
        "case_title": case_title,
        "court": court,
        "year": year,
        "case_number": case_number,
        "verdict": verdict,
        "petitioner": petitioner,
        "respondent": respondent,
        "issues": issues[:3],
        "sections_cited": sections_cited,
        "petitioner_arguments": pet_args[:4],
        "respondent_arguments": resp_args[:4],
        "summary": summary,
        "total_citations": len(citations),
    }


def _extract_arguments(text, party_keywords):
    """Extract key arguments made by a party."""
    args = []
    text_lower = text.lower()
    for kw in party_keywords:
        patterns = [
            rf"(?:learned\s+)?(?:counsel\s+)?(?:for\s+)?(?:the\s+)?{kw}\s+(?:submitted|argued|contended|urged|stated)\s+(?:that\s+)?([^\n\.]+[\.])".format(),
            rf"{kw}['s]*\s+(?:submission|argument|contention)\s+(?:is|was)\s+(?:that\s+)?([^\n\.]+[\.])".format(),
        ]
        for pat in patterns:
            for m in re.finditer(pat, text_lower):
                arg = m.group(1).strip().capitalize()
                if 20 < len(arg) < 200:
                    args.append(arg[:150])
                if len(args) >= 4:
                    return args
    return args


def _extract_clean_summary(text):
    """Extract a clean summary from the beginning of the judgment."""
    # Skip table of contents and headers — find first substantial paragraph
    paragraphs = text.split("\n")
    summary_parts = []
    char_count = 0
    started = False
    for para in paragraphs:
        stripped = para.strip()
        # Skip short lines (headers, page numbers, ToC lines with dots)
        if not stripped or len(stripped) < 40:
            continue
        if "....." in stripped or stripped.startswith("I.") or stripped.startswith("II."):
            continue
        # Skip lines that are all caps (headings)
        if stripped.isupper() and len(stripped) < 80:
            continue
        started = True
        summary_parts.append(stripped)
        char_count += len(stripped)
        if char_count > 600:
            break

    return " ".join(summary_parts)[:700] if summary_parts else text[:500]