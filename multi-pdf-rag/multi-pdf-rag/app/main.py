
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import BASE_DIR, TOP_K
from .llm import get_llm
from .pdf_processing import extract_pages, split_into_chunks
from .vector_store import VectorStore

app = FastAPI(title="Multi-PDF RAG")
store = VectorStore()

SYSTEM_PROMPT = (
    "You answer questions using ONLY the provided context excerpts "
    "from the user's PDFs. "
    "If the context does not contain the answer, reply exactly: "
    "\"I couldn't find that in the uploaded documents.\" "
    "Never use outside knowledge. "
    "Cite the sources you used inline like [file.pdf, p.3]."
)


class Question(BaseModel):
    question: str


@app.post("/api/upload")
def upload(files: list[UploadFile] = File(...)):
    results = []

    for f in files:
        name = f.filename or "unnamed.pdf"

        try:
            if not name.lower().endswith(".pdf"):
                raise ValueError("Not a PDF file.")

            pages = extract_pages(f.file.read(), name)

            if not pages:
                raise ValueError(
                    "No extractable text (scanned PDFs need OCR)."
                )

            chunks = split_into_chunks(pages)
            store.add_document(name, chunks)

            results.append({
                "name": name,
                "ok": True,
                "pages": len(pages),
                "chunks": len(chunks)
            })

        except Exception as e:
            results.append({
                "name": name,
                "ok": False,
                "error": str(e)
            })

    return {
        "results": results,
        "documents": store.list_documents()
    }


@app.get("/api/documents")
def documents():
    return {"documents": store.list_documents()}


@app.delete("/api/documents/{name}")
def delete_document(name: str):
    if not store.remove_document(name):
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {"documents": store.list_documents()}


@app.post("/api/ask")
def ask(body: Question):
    q = body.question.strip()

    if not q:
        raise HTTPException(
            status_code=400,
            detail="Ask a question first."
        )

    hits = store.search(q, TOP_K)

    if not hits:
        raise HTTPException(
            status_code=400,
            detail="Upload at least one PDF before asking questions."
        )

    context = "\n\n".join(
        f"[Source: {d.metadata['source']} | "
        f"Page: {d.metadata['page']}]\n{d.page_content}"
        for d, _ in hits
    )

    try:
        answer = get_llm().generate(
            SYSTEM_PROMPT,
            f"Context:\n{context}\n\nQuestion: {q}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM error: {str(e)}"
        )

    sources = []

    for d, score in hits:
        sources.append({
            "source": str(d.metadata["source"]),
            "page": int(d.metadata["page"]),
            "score": float(round(float(score), 3)),
            "snippet": str(d.page_content[:300])
        })

    return {
        "answer": str(answer),
        "sources": sources
    }


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)
