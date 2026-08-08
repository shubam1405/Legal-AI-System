CURRENT_DOCUMENTS = {}
CURRENT_CASE_NAMES = {}


def set_current_document(text: str, thread_id: str = "default", case_name: str = None):
    CURRENT_DOCUMENTS[thread_id] = text
    if case_name:
        CURRENT_CASE_NAMES[thread_id] = case_name


def get_current_document(thread_id: str = "default"):
    return CURRENT_DOCUMENTS.get(thread_id, "")


def get_current_case_name(thread_id: str = "default"):
    return CURRENT_CASE_NAMES.get(thread_id, "")