"""
Prompts for the lawyer matchmaking pipeline.
Used by matchmaking_service.py.
"""

__all__ = ["SPECIALIZATION_EXTRACTION_PROMPT", "LAWYER_RERANKING_PROMPT", "LEGAL_GUIDANCE_PROMPT"]

SPECIALIZATION_EXTRACTION_PROMPT = """You are a legal domain classifier.

Given the following case description, identify the relevant legal specializations
that a lawyer must have to handle this case effectively.

CASE DESCRIPTION:
{case_description}

Available specializations:
- Criminal Law
- Civil Law
- Family Law
- Labour Law
- Consumer Protection
- Property Law
- Corporate Law
- Constitutional Law
- Contract Law
- Intellectual Property
- Taxation
- Banking & Finance
- Immigration
- Cyber Law
- Environmental Law

Return a JSON array of the 1-3 most relevant specializations.
Example: ["Criminal Law", "Property Law"]

Return ONLY the JSON array. No explanation, no code blocks."""

LEGAL_GUIDANCE_PROMPT = """You are an expert in Indian law, especially the Indian Penal Code (IPC) and allied statutes.

A user has described the following legal problem:
{case_description}

Provide:
1. The most relevant IPC section(s) or other applicable Indian legal provisions, each with a short title (e.g. "Section 420 - Cheating")
2. Concrete remedies or next steps the person can take (e.g. filing an FIR, sending a legal notice, approaching consumer court)
3. A short, plain-language explanation of their situation (2-4 sentences, no legal jargon)

Be specific to Indian law. If you're not certain of an exact section number, say so rather than guessing confidently."""

LAWYER_RERANKING_PROMPT = """You are an expert legal matchmaker for Indian law.

A user needs legal help with the following case:
{case_description}

Here are {count} candidate lawyers retrieved from the database:
{candidates}

Rank the TOP 5 most suitable lawyers for this specific case.
Consider these criteria in order of priority:
1. Specialization match — does the lawyer's specialization directly match the case domain?
2. Experience — years of practice and cases handled
3. Success rate — higher is better
4. Rating — client satisfaction
5. Language — can the lawyer communicate in the user's preferred language?

Return a JSON array of exactly 5 entries (fewer if less than 5 candidates):
[
  {{
    "lawyer_id": "UUID string of the lawyer",
    "rank": 1,
    "reasoning": "2-3 sentence explanation of why this lawyer is the best match for this specific case"
  }},
  ...
]

Return ONLY the JSON array. No explanation, no code blocks."""
