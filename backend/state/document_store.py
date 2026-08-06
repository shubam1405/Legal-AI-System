CURRENT_DOCUMENTS = {}


def set_current_document(text: str, thread_id: str = "default"):
    CURRENT_DOCUMENTS[thread_id] = text


def get_current_document(thread_id: str = "default"):
    return CURRENT_DOCUMENTS.get(thread_id, "")