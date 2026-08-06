from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
import re
from backend.state.document_store import get_current_document


@tool
def analyze_current_case(config: RunnableConfig):
    """
    Analyze uploaded judgement and extract legal insights.
    """

    thread_id = config.get("configurable", {}).get("thread_id", "default")
    text = get_current_document(thread_id)

    if not text:
        return "No document uploaded."

    ipc_pattern = r"Section\s\d+"
    ipc_sections = list(set(re.findall(ipc_pattern, text)))

    case_pattern = r"[A-Z][A-Za-z\s\.]+ v\. [A-Z][A-Za-z\s\.]+"
    citations = list(set(re.findall(case_pattern, text)))

    summary = text[:1200]

    return {
        "summary": summary,
        "ipc_sections": ipc_sections,
        "precedents": citations[:10]
    }