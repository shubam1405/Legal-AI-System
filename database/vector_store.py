import chromadb
import uuid

# persistent vector database
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="legal_cases"
)


# ----------------------------
# STORE CHUNKS
# ----------------------------
def store_chunks(chunks, filename):

    documents = []
    metadatas = []
    ids = []

    case_name = filename.replace(".pdf", "")

    for i, chunk in enumerate(chunks):

        documents.append(chunk)

        metadatas.append({
            "case_name": case_name,
            "chunk_id": i,
            "source": filename
        })

        ids.append(str(uuid.uuid4()))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print("Stored", filename, "with", len(chunks), "chunks")


# ----------------------------
# SEARCH SIMILAR CASES
# ----------------------------
def find_similar_cases(query):

    results = collection.query(
        query_texts=[query],
        n_results=8
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    cases = {}

    for doc, meta in zip(documents, metadatas):

        case_name = meta["case_name"]

        if case_name not in cases:
            cases[case_name] = doc

    return cases


def find_similar_with_scores(query, n_results=5):
    """Return similar cases with distance scores for visualization."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    seen = {}
    for doc, meta, dist in zip(documents, metadatas, distances):
        case_name = meta["case_name"]
        similarity = round(max(0, 1 - dist) * 100, 1)
        if case_name not in seen or similarity > seen[case_name]["similarity"]:
            seen[case_name] = {
                "case_name": case_name,
                "similarity": similarity,
                "snippet": doc[:200]
            }

    return list(seen.values())