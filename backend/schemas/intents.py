from pydantic import BaseModel, Field
from typing import List

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
