
import PyPDF2


def load_pdf(file_path: str) -> str:
    """Load and extract text from a PDF file."""
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def load_document(file_path: str) -> str:
    """Load and extract text from a document based on its file extension."""
    if file_path.lower().endswith(".pdf"):
        return load_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}" )



