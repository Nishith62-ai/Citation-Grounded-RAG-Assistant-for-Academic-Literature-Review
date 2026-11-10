"""FAISS vector store persisted in data/vectorstore/."""
import threading
from collections import defaultdict
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from .config import VECTORSTORE_DIR, EMBEDDING_MODEL


class VectorStore:
    def __init__(self):
        # WHY EMBEDDINGS: a computer can't compare the *meaning* of text directly.
        # An embedding model turns each chunk into a list of numbers (a vector) so that
        # chunks with similar meaning end up close together. A question is embedded the
        # same way, and the nearest chunk vectors are the most relevant passages --
        # even when they share no exact keywords with the question.
        # This model runs locally on CPU; no API key needed.
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )
        self._lock = threading.Lock()
        self.db = None
        if (VECTORSTORE_DIR / "index.faiss").exists():
            # Safe: we only load an index this app wrote itself.
            self.db = FAISS.load_local(str(VECTORSTORE_DIR), self.embeddings,
                                       allow_dangerous_deserialization=True)

    def _save(self):
        self.db.save_local(str(VECTORSTORE_DIR))

    def _remove_unlocked(self, source: str) -> bool:
        if self.db is None:
            return False
        ids = [i for i, d in self.db.docstore._dict.items() if d.metadata.get("source") == source]
        if ids:
            self.db.delete(ids)
        return bool(ids)

    def add_document(self, source: str, chunks):
        """Index chunks for one PDF. Re-uploading a filename replaces the old version."""
        with self._lock:
            self._remove_unlocked(source)
            if self.db is None:
                self.db = FAISS.from_documents(chunks, self.embeddings)
            else:
                self.db.add_documents(chunks)
            self._save()

    def remove_document(self, source: str) -> bool:
        with self._lock:
            removed = self._remove_unlocked(source)
            if removed:
                self._save()
            return removed

    def list_documents(self):
        stats = defaultdict(lambda: {"chunks": 0, "pages": set()})
        if self.db:
            for d in self.db.docstore._dict.values():
                s = stats[d.metadata["source"]]
                s["chunks"] += 1
                s["pages"].add(d.metadata["page"])
        return [{"name": n, "chunks": s["chunks"], "pages": len(s["pages"])}
                for n, s in sorted(stats.items())]

    def search(self, question: str, k: int):
        """Return [(chunk, similarity 0..1)] for the k most similar chunks."""
        if not self.db or not self.list_documents():
            return []
        results = self.db.similarity_search_with_score(question, k=k)
        # FAISS returns squared L2 distance; for unit vectors cosine = 1 - d/2.
        return [(doc, max(0.0, 1 - dist / 2)) for doc, dist in results]
