"""PDF -> page-level Documents -> chunks. Metadata (source, page) is kept throughout."""
import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_pages(data: bytes, filename: str) -> list[Document]:
    """One Document per page, so we never lose which page text came from."""
    pages = []
    with fitz.open(stream=data, filetype="pdf") as pdf:
        for number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if text:  # skip blank / image-only pages
                pages.append(Document(page_content=text,
                                      metadata={"source": filename, "page": number}))
    return pages


def split_into_chunks(pages: list[Document]) -> list[Document]:
    """Split pages into overlapping chunks. split_documents copies each page's
    metadata onto every chunk, so chunks still know their PDF and page."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(pages)
