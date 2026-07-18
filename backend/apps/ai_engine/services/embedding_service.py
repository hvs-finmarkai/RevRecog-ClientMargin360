import uuid
from typing import Optional
from dataclasses import dataclass, asdict

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


@dataclass
class SearchResult:
    document_id: str
    content: str
    metadata: dict
    similarity_score: float
    source_file: str = ""
    chunk_index: int = 0

    def to_dict(self):
        return asdict(self)


@dataclass
class DocumentChunk:
    chunk_id: str
    content: str
    metadata: dict
    embedding: list = None

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
        }


class EmbeddingService:
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    DEFAULT_CHUNK_SIZE = 512
    DEFAULT_CHUNK_OVERLAP = 50

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        persist_directory: str = "./chroma_db",
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False,
        ))
        self.persist_directory = persist_directory

    def get_or_create_collection(self, collection_name: str):
        return self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def index_document(self, document_text: str, metadata: dict, collection_name: str = "contracts") -> list:
        chunks = self._chunk_document(document_text, metadata)
        collection = self.get_or_create_collection(collection_name)

        chunk_ids = []
        batch_size = 100

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.content for chunk in batch]
            metadatas = [chunk.metadata for chunk in batch]
            embeddings = self.model.encode(documents).tolist()

            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
            chunk_ids.extend(ids)

        return chunk_ids

    def index_documents_batch(self, documents: list, collection_name: str = "contracts") -> dict:
        results = {"indexed": 0, "failed": 0, "chunk_ids": []}

        for doc in documents:
            try:
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})
                ids = self.index_document(text, metadata, collection_name)
                results["indexed"] += 1
                results["chunk_ids"].extend(ids)
            except Exception:
                results["failed"] += 1

        return results

    def search_similar(self, query: str, collection_name: str = "contracts", top_k: int = 5, filters: Optional[dict] = None) -> list:
        collection = self.get_or_create_collection(collection_name)
        query_embedding = self.model.encode([query]).tolist()

        search_params = {
            "query_embeddings": query_embedding,
            "n_results": top_k,
        }

        if filters:
            search_params["where"] = filters

        results = collection.query(**search_params)

        search_results = []
        if results and results["ids"] and results["ids"][0]:
            for idx in range(len(results["ids"][0])):
                distance = results["distances"][0][idx] if results.get("distances") else 0
                similarity = 1 - distance

                metadata = results["metadatas"][0][idx] if results.get("metadatas") else {}

                search_results.append(SearchResult(
                    document_id=results["ids"][0][idx],
                    content=results["documents"][0][idx] if results.get("documents") else "",
                    metadata=metadata,
                    similarity_score=round(similarity, 4),
                    source_file=metadata.get("source_file", ""),
                    chunk_index=metadata.get("chunk_index", 0),
                ))

        return search_results

    def search_contract_clauses(self, clause_query: str, client_id: Optional[str] = None, top_k: int = 5) -> list:
        filters = None
        if client_id:
            filters = {"client_id": client_id}
        return self.search_similar(clause_query, collection_name="contracts", top_k=top_k, filters=filters)

    def semantic_search(self, query: str, collection_names: Optional[list] = None, top_k: int = 10) -> list:
        if collection_names is None:
            collection_names = ["contracts", "invoices", "proposals", "communications"]

        all_results = []
        per_collection_limit = max(3, top_k // len(collection_names))

        for collection_name in collection_names:
            try:
                results = self.search_similar(query, collection_name, top_k=per_collection_limit)
                for result in results:
                    result.metadata["collection"] = collection_name
                all_results.extend(results)
            except Exception:
                continue

        all_results.sort(key=lambda r: r.similarity_score, reverse=True)
        return all_results[:top_k]

    def delete_document(self, document_id: str, collection_name: str = "contracts"):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=[document_id])

    def delete_by_metadata(self, filters: dict, collection_name: str = "contracts"):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(where=filters)

    def get_document_chunks(self, source_file: str, collection_name: str = "contracts") -> list:
        collection = self.get_or_create_collection(collection_name)
        results = collection.get(where={"source_file": source_file})

        chunks = []
        if results and results["ids"]:
            for idx in range(len(results["ids"])):
                chunks.append(DocumentChunk(
                    chunk_id=results["ids"][idx],
                    content=results["documents"][idx] if results.get("documents") else "",
                    metadata=results["metadatas"][idx] if results.get("metadatas") else {},
                ))

        chunks.sort(key=lambda c: c.metadata.get("chunk_index", 0))
        return chunks

    def _chunk_document(self, text: str, metadata: dict) -> list:
        chunks = []
        sentences = self._split_into_sentences(text)

        current_chunk = ""
        current_length = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())

            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_metadata = {
                    **metadata,
                    "chunk_index": chunk_index,
                    "chunk_length": current_length,
                }
                chunks.append(DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    content=current_chunk.strip(),
                    metadata=chunk_metadata,
                ))

                overlap_words = current_chunk.split()[-self.chunk_overlap:]
                current_chunk = " ".join(overlap_words) + " " + sentence
                current_length = len(current_chunk.split())
                chunk_index += 1
            else:
                current_chunk += " " + sentence
                current_length += sentence_length

        if current_chunk.strip():
            chunk_metadata = {
                **metadata,
                "chunk_index": chunk_index,
                "chunk_length": current_length,
            }
            chunks.append(DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                content=current_chunk.strip(),
                metadata=chunk_metadata,
            ))

        return chunks

    def _split_into_sentences(self, text: str) -> list:
        import re
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        embeddings = self.model.encode([text_a, text_b])
        from numpy import dot
        from numpy.linalg import norm
        similarity = dot(embeddings[0], embeddings[1]) / (norm(embeddings[0]) * norm(embeddings[1]))
        return float(similarity)

    def get_collection_stats(self, collection_name: str = "contracts") -> dict:
        collection = self.get_or_create_collection(collection_name)
        count = collection.count()
        return {
            "collection_name": collection_name,
            "document_count": count,
        }
