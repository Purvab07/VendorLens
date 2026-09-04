import os
import re
import requests
from pypdf import PdfReader


def load_document(filepath: str) -> str:
    """Reads a plain text file and returns its content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def extract_text_from_pdf(filepath: str) -> str:
    """Extracts all text from a PDF file."""
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_gdoc(share_url: str) -> str:
    """
    Fetches text from a Google Doc, given its shareable link.
    The doc must be shared as 'Anyone with the link can view'.
    """
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", share_url)
    if not match:
        raise ValueError("Could not find a valid Google Doc ID in that URL.")

    doc_id = match.group(1)
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"

    response = requests.get(export_url)
    if response.status_code != 200:
        raise ValueError(
            "Could not fetch the Google Doc. Make sure it's shared as "
            "'Anyone with the link can view'."
        )
    return response.text


def load_any_document(source: str, source_type: str) -> str:
    """
    Dispatches to the right loader based on source_type: 'txt', 'pdf', or 'gdoc'.
    'source' is a filepath for txt/pdf, or a share URL for gdoc.
    """
    if source_type == "txt":
        return load_document(source)
    elif source_type == "pdf":
        return extract_text_from_pdf(source)
    elif source_type == "gdoc":
        return extract_text_from_gdoc(source)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    start = 0
    chunks = []
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def load_and_chunk(filepath: str) -> list[str]:
    """Kept for backward compatibility — assumes a plain text file path."""
    text = load_document(filepath)
    return chunk_text(text)


def load_and_chunk_any(source: str, source_type: str) -> list[str]:
    """New general version: loads from txt, pdf, or gdoc, then chunks."""
    text = load_any_document(source, source_type)
    return chunk_text(text)


if __name__ == "__main__":
    test_file = "data/regulations/cfpb_complaint_handling.txt"
    if os.path.exists(test_file):
        chunks = load_and_chunk(test_file)
        print(f"Loaded {len(chunks)} chunks")
        print("First chunk preview:", chunks[0][:200])
    else:
        print(f"No file found at {test_file} — add a sample .txt file there first")