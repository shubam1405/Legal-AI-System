import sys
import os

# add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion_pipeline.parser import parse_pdf
from ingestion_pipeline.text_splitter import split_text
from database.vector_store import store_chunks


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASE_FOLDER = os.path.join(BASE_DIR, "docs", "cases")


def index_cases():

    files = os.listdir(CASE_FOLDER)

    print("Files found:", files)
    print()

    for file in files:

        if not file.lower().endswith(".pdf"):
            continue

        try:

            path = os.path.join(CASE_FOLDER, file)

            print(f"Processing {file}")

            with open(path, "rb") as f:

                text = parse_pdf(f)

            chunks = split_text(text)

            store_chunks(chunks, file)

            print(f"Stored {file} with {len(chunks)} chunks\n")

        except Exception as e:

            print(f"Error processing {file}: {e}\n")


if __name__ == "__main__":
    index_cases()