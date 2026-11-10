# Multi-PDF RAG

Upload several PDFs and ask questions; answers are grounded only in your documents, with PDF and page sources shown.

## Run
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then add your OPENAI_API_KEY
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## How it works
PyMuPDF extracts text per page -> RecursiveCharacterTextSplitter makes chunks (metadata kept) -> local MiniLM embeddings -> FAISS index saved in `data/vectorstore/` -> top-K similar chunks go to the LLM with a "use only this context" prompt.

## Customize
- Chunk size, overlap, top-K, models: `app/config.py` or `.env`
- New LLM provider: subclass `LLMProvider` in `app/llm.py`, add to `PROVIDERS`, set `LLM_PROVIDER`

## Notes
- Scanned (image-only) PDFs have no extractable text and need OCR first.
- Re-uploading a filename replaces its previous chunks.
- The first upload downloads the embedding model (~90 MB) once.
