from pydantic import BaseModel, Field
from typing import List, Optional

class ChatIntentClassification(BaseModel):
    intent: str = Field(
        description="One of: 'SIMILAR_CASE' (find cases similar to a fact pattern), "
                    "'DIRECT_CASE_SEARCH' (a named case, e.g. 'X v. Y'), "
                    "'LEGAL_KNOWLEDGE' (a general legal question, no case search needed), "
                    "'LEGAL_RESEARCH' (asking about a law, statute, or legal concept in depth), "
                    "'CLARIFICATION' (the query is too vague/ambiguous to act on)."
    )
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    reasoning: str = Field(description="Brief reasoning for why this intent was chosen.")


class CaseQueryExtraction(BaseModel):
    case_name: Optional[str] = Field(default=None, description="Case name if a specific case was named, e.g. 'State of Haryana v. Bhajan Lal'.")
    case_number: Optional[str] = Field(default=None, description="Case/citation number if mentioned.")
    court: Optional[str] = Field(default=None, description="Court name if mentioned.")
    year: Optional[int] = Field(default=None, description="Year if mentioned.")
    case_facts: Optional[str] = Field(default=None, description="For similar-case searches: the fact pattern to search for.")
    search_query: str = Field(description="A clean, standalone search query built from the above, suitable for searching a case archive or the web.")


class IntentClassification(BaseModel):
    intent: str = Field(
        description="The classified intent of the user query. Should be one of: 'lawyer_match', 'document_qa', 'legal_template', 'case_analysis', 'general_chat'."
    )
    confidence: float = Field(
        description="Confidence score of the classification between 0.0 and 1.0."
    )
    reasoning: str = Field(
        description="Brief reasoning for why this intent was chosen."
    )

class LawyerSpecializationExtraction(BaseModel):
    specializations: List[str] = Field(
        description="List of legal specializations extracted from the case description."
    )

class LawyerMatchResult(BaseModel):
    lawyer_ids: List[str] = Field(
        description="List of matched lawyer UUIDs based on the query."
    )
    explanation: str = Field(
        description="Explanation of why these lawyers were matched."
    )

class LegalGuidance(BaseModel):
    applicable_sections: List[str] = Field(
        description="Relevant IPC sections or other applicable Indian legal provisions, "
                    "each with a short title, e.g. 'Section 420 - Cheating'."
    )
    remedies: List[str] = Field(
        description="Concrete remedies or next steps the person can take, e.g. "
                    "'File an FIR at the local police station', 'Send a legal notice'."
    )
    explanation: str = Field(
        description="A short, plain-language explanation of the legal situation (2-4 sentences, no jargon)."
    )


class CaseAnalysisResult(BaseModel):
    summary: str = Field(
        description="A concise summary of the case."
    )
    applicable_ipc_sections: List[str] = Field(
        description="List of applicable IPC sections based on the case details."
    )
    analysis: str = Field(
        description="Detailed legal analysis and implications."
    )
