import os
import chromadb
from typing import List, Dict, Any

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

class ChromaService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name="historical_events",
            metadata={"hnsw:space": "cosine"}
        )

    def add_events(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query_similar_events(self, query_embedding: List[float], n_results: int = 4) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        matches = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                meta = results["metadatas"][0][i]
                doc = results["documents"][0][i]
                dist = results["distances"][0][i] if "distances" in results else 0.5
                similarity = round(1.0 - float(dist), 3)
                matches.append({
                    "id": results["ids"][0][i],
                    "title": meta.get("title", "Unknown Event"),
                    "date": meta.get("date", "Unknown Date"),
                    "description": doc,
                    "sector": meta.get("sector", "General"),
                    "outcome": meta.get("outcome", "No outcome detailed"),
                    "similarity_score": similarity
                })
        return matches