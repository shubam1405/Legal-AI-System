import re
from langchain_core.tools import tool

# this will store the latest uploaded document
CURRENT_DOCUMENT = ""


def set_document_text(text):
    global CURRENT_DOCUMENT
    CURRENT_DOCUMENT = text


@tool
def summarize_document() -> str:
    """
    Generate a summary of the uploaded legal judgment.
    """
    return CURRENT_DOCUMENT[:3000]


@tool
def extract_ipc_sections() -> list:
    """
    Extract IPC sections mentioned in the document.
    """

    pattern = r"Section\s\d+"

    matches = re.findall(pattern, CURRENT_DOCUMENT)

    return list(set(matches))


@tool
def extract_case_citations() -> list:
    """
    Extract case precedents cited in the judgment.
    """

    pattern = r"[A-Z][A-Za-z\s\.&]+ v\. [A-Z][A-Za-z\s\.&]+"

    matches = re.findall(pattern, CURRENT_DOCUMENT)

    cleaned = [m.replace("\n", " ").strip() for m in matches]

    return list(set(cleaned))


@tool
def generate_case_brief() -> str:
    """
    Generate a structured case brief from the uploaded judgment.
    """

    text = CURRENT_DOCUMENT[:6000]

    return f"""
Analyze the following Supreme Court judgment and create a legal case brief.

Judgment:
{text}

Return the result in the following structure:

Case Name:
Facts:
Issues:
Arguments:
Court Reasoning:
Final Judgment:
Legal Principles:
"""