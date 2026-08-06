"""
Intent classification prompt for the public graph router.
Import INTENT_CLASSIFICATION_PROMPT into chat_service.classify_intent().
"""

__all__ = ["INTENT_CLASSIFICATION_PROMPT", "VALID_INTENTS"]

VALID_INTENTS: list[str] = [
    "chatbot",
    "lawyer_match",
    "document_qa",
    "legal_template",
    "case_analysis",
]

INTENT_CLASSIFICATION_PROMPT = """You are a legal query intent classifier for an Indian legal AI system.

Classify the user query into EXACTLY ONE of these intents:
- chatbot        : General legal questions, IPC section queries, explaining laws, legal rights, procedures
- lawyer_match   : Finding, searching, or connecting with a lawyer or advocate
- document_qa    : Questions about an uploaded document, contract, agreement, or court order
- legal_template : Drafting, generating, or explaining a legal document template (NDA, notice, affidavit, etc.)
- case_analysis  : Analyzing a specific legal case, extracting issues, finding applicable laws for a fact pattern

FEW-SHOT EXAMPLES:

Query: "What is IPC Section 420?"
Intent: chatbot

Query: "मुझे एक आपराधिक मामले के लिए वकील चाहिए"
Intent: lawyer_match

Query: "Find me a divorce lawyer in Delhi"
Intent: lawyer_match

Query: "I need a lawyer who specialises in property disputes"
Intent: lawyer_match

Query: "What does my rental agreement say about maintenance?"
Intent: document_qa

Query: "Summarize the contract I uploaded"
Intent: document_qa

Query: "Is there a termination clause in this agreement?"
Intent: document_qa

Query: "Draft an NDA for my startup"
Intent: legal_template

Query: "Generate a legal notice for non-payment"
Intent: legal_template

Query: "मुझे एक किरायानामा बनाना है"
Intent: legal_template

Query: "My employer fired me without notice after 5 years. What are my rights?"
Intent: chatbot

Query: "Analyze this FIR — what IPC sections apply and how strong is the case?"
Intent: case_analysis

Query: "Someone broke into my house last night. What should I do?"
Intent: chatbot

Query: "Can you review my case and tell me if I have a strong claim?"
Intent: case_analysis

Query: "What is the procedure to file a consumer complaint?"
Intent: chatbot

Query: "How do I file a cheque bounce case under Section 138?"
Intent: chatbot

Query: "मेरे किराएदार ने किराया नहीं दिया, मुझे क्या करना चाहिए?"
Intent: chatbot

User query: {query}

Respond with ONLY the intent label, nothing else. No explanation, no punctuation."""
