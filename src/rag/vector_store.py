"""Índice vetorial local da base de conhecimento (ChromaDB + embeddings multilingues).

Modelo: intfloat/multilingual-e5-small (sentence-transformers, execução local em CPU).
O modelo E5 exige prefixos distintos para documentos ("passage: ") e pesquisas ("query: ").
Os embeddings são calculados aqui e passados explicitamente ao ChromaDB (sem função de
embedding por omissão), garantindo que indexação e pesquisa usam exatamente o mesmo modelo.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.rag.kb_parser import Section

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "intfloat/multilingual-e5-small"
DEFAULT_COLLECTION = "swaglabs_kb"


@dataclass(frozen=True)
class Hit:
    chunk_id: str
    section_number: int
    section_title: str
    score: float  # semelhança de cosseno (1 = idêntico)
    content: str
    metadata: dict[str, Any]


class KnowledgeStore:
    def __init__(self, path: Path, collection: str = DEFAULT_COLLECTION, model_name: str = DEFAULT_MODEL) -> None:
        self._client = chromadb.PersistentClient(path=str(path), settings=ChromaSettings(anonymized_telemetry=False))
        self._collection_name = collection
        self.model_name = model_name
        self._model: SentenceTransformer | None = None
        self._coll: chromadb.Collection | None = None

    # -- embeddings -------------------------------------------------------------
    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # import tardio (pesado)

            self._model = SentenceTransformer(self.model_name, device="cpu")
        return self._model

    def _embed(self, texts: list[str], prefix: str) -> list[list[float]]:
        vectors = self.model.encode([prefix + t for t in texts], normalize_embeddings=True, show_progress_bar=False)
        return [v.tolist() for v in vectors]

    # -- coleção ----------------------------------------------------------------
    def _collection(self) -> chromadb.Collection:
        if self._coll is None:
            self._coll = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=None,
            )
        return self._coll

    def rebuild(self, sections: list[Section], source: dict[str, str | int]) -> int:
        """Recria a coleção a partir das secções (operação idempotente). Devolve o n.º de blocos."""
        existing = [getattr(c, "name", c) for c in self._client.list_collections()]
        if self._collection_name in existing:
            self._client.delete_collection(self._collection_name)
        self._coll = None
        collection = self._collection()
        collection.add(
            ids=[s.chunk_id for s in sections],
            embeddings=self._embed([s.content for s in sections], "passage: "),
            documents=[s.content for s in sections],
            metadatas=[
                {
                    "section_number": s.number,
                    "section_title": s.title,
                    "url_path": s.url_path or "",
                    "rule_ids": ",".join(s.rule_ids),
                    "embedding_model": self.model_name,
                    **source,
                }
                for s in sections
            ],
        )
        return collection.count()

    def query(self, text: str, k: int = 5, exclude_sections: tuple[int, ...] = ()) -> list[Hit]:
        """Pesquisa semântica. `exclude_sections` retira secções do ranking (ex.: a secção 0,
        que é sempre incluída no contexto por get_section)."""
        collection = self._collection()
        if collection.count() == 0:
            raise RuntimeError("índice vazio: executar a ingestão primeiro")
        where = {"section_number": {"$nin": list(exclude_sections)}} if exclude_sections else None
        res = collection.query(
            query_embeddings=self._embed([text], "query: "),
            n_results=min(k, collection.count() - len(exclude_sections)),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return [
            self._hit(cid, doc, meta, 1.0 - float(dist))
            for cid, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])
        ]

    def get_section(self, number: int) -> Hit:
        """Obtém uma secção pelo número (sem pesquisa)."""
        res = self._collection().get(where={"section_number": number}, include=["documents", "metadatas"])
        if not res["ids"]:
            raise KeyError(f"secção {number} não indexada")
        return self._hit(res["ids"][0], res["documents"][0], res["metadatas"][0], 1.0)

    @staticmethod
    def _hit(cid: str, doc: str, meta: Any, score: float) -> Hit:
        return Hit(
            chunk_id=cid,
            section_number=int(meta["section_number"]),
            section_title=str(meta["section_title"]),
            score=round(score, 4),
            content=doc,
            metadata=dict(meta),
        )
