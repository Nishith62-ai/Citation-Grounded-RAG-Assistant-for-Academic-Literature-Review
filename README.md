# Citation-Grounded RAG Assistant for Academic Literature Review

An AI-powered **Multi-PDF Retrieval-Augmented Generation (RAG) application** that allows users to upload multiple research papers and PDF documents, ask questions in natural language, and receive context-aware answers backed by document references and page citations.

Instead of relying entirely on an LLM's general knowledge, the application retrieves relevant information from uploaded documents and uses that context to generate answers.

## Key Features

- **Multi-PDF Upload:** Upload and manage multiple PDF documents.
- **Intelligent Document Processing:** Extract text from PDFs and split it into smaller, searchable chunks.
- **Semantic Search:** Find relevant information using Hugging Face sentence embeddings and FAISS vector search.
- **Context-Grounded Answers:** Generate answers using retrieved document content rather than unrelated external knowledge.
- **Source Citations:** Display source PDF filenames and page numbers alongside answers.
- **Document Management:** View uploaded documents and remove individual documents.
- **Persistent Vector Storage:** Store document embeddings locally for reuse.
- **LLM Integration:** Support for Google Gemini and OpenAI through a provider-based architecture.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| PDF Processing | PyMuPDF |
| Text Chunking | LangChain |
| Embedding Model | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Database | FAISS |
| LLM | Google Gemini / OpenAI |
| Frontend | HTML, CSS, JavaScript |
| API Server | Uvicorn |

## System Architecture

```text
        PDF Documents
              |
              v
       PDF Text Extraction
           (PyMuPDF)
              |
              v
        Text Chunking
         (LangChain)
              |
              v
       Text Embeddings
    (Hugging Face MiniLM)
              |
              v
        FAISS Vector Store
              |
              |
User Question |
      |       |
      v       v
   Semantic Similarity Search
              |
              v
       Top-K Relevant Chunks
              |
              v
       LLM Context + Prompt
        (Gemini / OpenAI)
              |
              v
       Context-Grounded Answer
              |
              v
       Answer + Source Citations
```

## How It Works

1. **Upload:** Users upload one or more PDF documents through the application.
2. **Extraction:** PyMuPDF extracts text from each PDF while preserving page metadata.
3. **Chunking:** LangChain's RecursiveCharacterTextSplitter divides extracted text into manageable chunks with overlapping content.
4. **Embedding:** Sentence Transformers converts each chunk into a numerical vector representation.
5. **Indexing:** FAISS stores the vectors locally and enables efficient similarity searches.
6. **Retrieval:** When a question is submitted, the application retrieves the most relevant document chunks.
7. **Generation:** The retrieved content is passed to the configured LLM with instructions to answer using only the supplied context.
8. **Citation:** The response includes source document names and page references.

## Project Structure

```text
Citation-Grounded-RAG-Assistant/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── llm.py
│   ├── main.py
│   ├── pdf_processing.py
│   └── vector_store.py
│
├── data/
│   └── vectorstore/
│
├── static/
│   └── index.html
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Nishith62-ai/Citation-Grounded-RAG-Assistant-for-Academic-Literature-Review.git

cd Citation-Grounded-RAG-Assistant-for-Academic-Literature-Review
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

For Git Bash:

```bash
source venv/Scripts/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

For Google Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
```

Keep your API key private. Never commit `.env` to GitHub.

### 5. Run the Application

```bash
python -m uvicorn app.main:app --reload
```

Open the application:

**http://127.0.0.1:8000**

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload` | Upload multiple PDF documents |
| GET | `/api/documents` | Retrieve uploaded document details |
| DELETE | `/api/documents/{name}` | Remove a document |
| POST | `/api/ask` | Ask questions about uploaded documents |

Interactive API documentation:

**http://127.0.0.1:8000/docs**

## Configuration

Application settings can be customized through `app/config.py` or environment variables.

| Parameter | Default | Purpose |
|---|---:|---|
| CHUNK_SIZE | 1000 | Number of characters per chunk |
| CHUNK_OVERLAP | 200 | Overlapping characters between chunks |
| TOP_K | 5 | Number of relevant chunks retrieved |
| EMBEDDING_MODEL | all-MiniLM-L6-v2 | Text embedding model |
| LLM_PROVIDER | gemini | Selected LLM provider |

## Limitations

- Scanned or image-only PDFs require OCR before text extraction.
- Answer quality depends on PDF text quality and retrieval relevance.
- The embedding model is downloaded during its first use.
- LLM responses depend on the availability and limits of the configured API provider.
- The vector database is stored locally and is not a hosted database.

## Future Enhancements

- OCR support for scanned PDF documents.
- Improved retrieval using reranking techniques.
- Support for additional document formats.
- Conversation history and multi-turn question answering.
- Advanced citation validation and retrieval evaluation.
- Docker-based deployment and CI/CD integration.

## Author

**Nishith Darsi**

B.Tech – Computer Science and Engineering (AI & ML)

Dayananda Sagar University

GitHub: [Nishith62-ai](https://github.com/Nishith62-ai)

---

*Built to make academic research and multi-document knowledge discovery more accessible through Retrieval-Augmented Generation.*
