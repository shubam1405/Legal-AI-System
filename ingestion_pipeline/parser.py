import fitz  # pymupdf


def parse_pdf(file):

    # If bytes already
    if isinstance(file, bytes):
        pdf_bytes = file

    # If file object
    elif hasattr(file, "read"):
        pdf_bytes = file.read()

    else:
        raise ValueError("Invalid PDF input")

    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""

    for page in pdf:
        text += page.get_text()

    return text