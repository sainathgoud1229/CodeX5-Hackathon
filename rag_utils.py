import ollama
import faiss
import numpy as np
from typing import List, Dict, Any

EMBED_MODEL = "nomic-embed-text:latest"

def get_embedding(text: str) -> np.ndarray:
    """
    Generates embedding vector for a given text string using local nomic-embed-text model.
    """
    try:
        response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
        embedding = response.get("embedding", [])
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        # Fallback dummy embedding of dimension 768 if call fails
        print(f"Warning: embedding call failed ({str(e)}), using zero fallback vector.")
        return np.zeros(768, dtype=np.float32)


class ClauseVectorStore:
    """
    In-memory FAISS vector index wrapper for fast document clause similarity search.
    """
    def __init__(self):
        self.index = None
        self.clauses = []
        self.dimension = None

    def build_index(self, clauses: List[Dict[str, Any]]):
        """
        Embeds all document clauses and populates the FAISS IndexFlatL2 index.
        """
        self.clauses = clauses
        if not clauses:
            return

        embeddings_list = []
        for clause in clauses:
            # Combine title + header + text for rich context embedding
            chunk_content = f"{clause['title']}\n{clause['text']}"
            vec = get_embedding(chunk_content)
            embeddings_list.append(vec)

        embeddings_matrix = np.vstack(embeddings_list)
        self.dimension = embeddings_matrix.shape[1]
        
        # Normalize vectors for Cosine Similarity (using IndexFlatIP)
        faiss.normalize_L2(embeddings_matrix)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings_matrix)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Queries the FAISS index and returns top-k matching clauses.
        """
        if self.index is None or not self.clauses:
            return []

        query_vec = get_embedding(query)
        query_vec = np.expand_dims(query_vec, axis=0)
        faiss.normalize_L2(query_vec)

        k = min(top_k, len(self.clauses))
        distances, indices = self.index.search(query_vec, k)

        results = []
        for idx, score in zip(indices[0], distances[0]):
            if 0 <= idx < len(self.clauses):
                clause_copy = dict(self.clauses[idx])
                clause_copy["similarity_score"] = float(score)
                results.append(clause_copy)

        return results
