"""
One-off script: resets the `legal_cases` Chroma collection (the one
used by database/vector_store.py / streamlit_app.py's PDF uploader),
which accumulated duplicate chunks due to the re-upload-on-every-message
bug in streamlit_app.py.

Run this once from the project root:
    python reset_legal_cases_collection.py

After running it, re-upload your PDF(s) in streamlit_app.py to repopulate
the collection cleanly (the file_id fix means it'll only index once now).
"""
import chromadb

client = chromadb.PersistentClient(path="chroma_db")

existing = [c.name for c in client.list_collections()]
if "legal_cases" in existing:
    client.delete_collection("legal_cases")
    print("Deleted 'legal_cases' collection.")
else:
    print("'legal_cases' collection doesn't exist — nothing to delete.")

# Recreate it empty so the app doesn't error on next run before a re-upload.
client.get_or_create_collection(name="legal_cases")
print("Recreated empty 'legal_cases' collection. You can now re-upload your PDF(s).")
