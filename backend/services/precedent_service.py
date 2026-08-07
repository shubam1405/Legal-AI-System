"""
Precedent lookup service.

Two lookup modes:
1. find_case()          -> direct lookup of a NAMED case ("X v. Y"),
                           backed by bharat_courts.ArchiveClient — free,
                           no API key, reads the public AWS Open Data
                           archive of SCI (1950-present) + all High Courts.
2. search_similar_cases() -> free-text similarity search over the local
                           Chroma index of previously ingested judgment
                           PDFs (see database/vector_store.py).

find_case() is for "what is case X" queries. search_similar_cases() is
for "find cases like this fact pattern" queries. Step 2 of this project
(similar-case search) will build a proper offline index for the second
mode; for now it stays as the narrow local-only fallback it already was.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import re
from typing import Any

from database.vector_store import find_similar_cases

__all__ = ["PrecedentService"]

_CASE_NAME_PATTERN = re.compile(
    r"([A-Z][A-Za-z.\s]{2,60}?)\s+(?:v\.|vs\.?|versus)\s+([A-Z][A-Za-z.\s]{2,60})",
    re.IGNORECASE,
)


def _extract_parties(query: str) -> tuple[str, str] | None:
    """Pulls (petitioner, respondent) out of an 'X v. Y' style query."""
    match = _CASE_NAME_PATTERN.search(query)
    if not match:
        return None
    return match.group(1).strip(" .,"), match.group(2).strip(" .,")


def _run_async(coro):
    """
    Runs an async coroutine from sync code, safely, whether or not this
    thread already has a running event loop (FastAPI's async endpoints
    do; a plain script doesn't).
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(coro)).result()


class PrecedentService:
    """Service for finding precedents: direct case lookup + similarity search."""

    def find_case(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Direct lookup of a named case, e.g. "State of Haryana v. Bhajan Lal".

        Backed by the free bharat_courts archive (SCI + all High Courts).
        Returns [] if the query isn't a recognizable case name, the
        archive has nothing, or bharat_courts isn't installed — callers
        should fall back to search_similar_cases() in that case.
        """
        parties = _extract_parties(query)
        if not parties:
            return []

        petitioner, respondent = parties

        try:
            from bharat_courts import ArchiveClient
        except ImportError:
            return []

        async def _search() -> list:
            async with ArchiveClient() as client:
                results = await client.search(party=petitioner, limit=limit)
                if not results:
                    results = await client.search(party=respondent, limit=limit)
                return results

        try:
            judgments = _run_async(_search())
        except Exception:
            return []

        results = []
        for j in judgments:
            court = getattr(j, "court_name", None) or getattr(j, "court", "")
            date = getattr(j, "decision_date", "")
            citation = getattr(j, "citation", "") or ""
            results.append({
                "case_name": getattr(j, "title", None) or f"{petitioner} v. {respondent}",
                "excerpt": " — ".join(str(p) for p in (court, date, citation) if p),
                "source": "bharat_courts_archive",
                "case_id": getattr(j, "case_id", "") or getattr(j, "cnr", ""),
            })
        return results

    def search_similar_cases(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find precedents relevant to a query or case description.

        Uses the SimilarCaseService which enforces the separation:
          - ChromaDB for vector similarity search (embeddings only)
          - PostgreSQL for metadata lookup (no embeddings)

        Falls back to the old local Chroma index if the new service
        returns no results.

        Args:
            query: The user's question or case description.
            top_k: Max number of distinct cases to return.

        Returns:
            List of {case_name, excerpt, source, ...} dicts, most relevant first.
        """
        try:
            from backend.services.similar_case_service import SimilarCaseService
            from backend.database.database import SessionLocal

            db = SessionLocal()
            try:
                service = SimilarCaseService(db)
                results = service.search_similar(query, top_k=top_k)
                if results:
                    return [
                        {
                            "case_name": r["case_name"],
                            "excerpt": (r.get("summary") or "")[:600],
                            "source": r.get("source", "local_index"),
                            "court_name": r.get("court_name"),
                            "decision_date": r.get("decision_date"),
                            "similarity_score": r.get("similarity_score", 0.0),
                        }
                        for r in results
                    ]
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to old local-only Chroma index
        try:
            cases = find_similar_cases(query)
        except Exception:
            return []

        results = []
        for case_name, excerpt in list(cases.items())[:top_k]:
            results.append({
                "case_name": case_name,
                "excerpt": excerpt[:600],
                "source": "local_index",
            })
        return results

