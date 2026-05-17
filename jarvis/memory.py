import numpy as np
import sqlite3
from fastembed import TextEmbedding

from jarvis.config import MEMORY_RETRIEVE_TOP_K


class Memory:
    def __init__(self, db_path: str, embed_model: str = 'BAAI/bge-small-en-v1.5'):
        self._database = sqlite3.connect(db_path, check_same_thread=False, timeout=5)
        self._database.execute('PRAGMA journal_mode=WAL')
        self._init_tables()

        self._embedder = TextEmbedding(model_name=embed_model)

        rows = self._database.execute(
            "SELECT id, vector FROM memories WHERE vector IS NOT NULL ORDER BY id"
        ).fetchall()
        if rows:
            self._idx_ids = [r[0] for r in rows]
            self._idx_vecs = np.array(
                [np.frombuffer(r[1], dtype=np.float32) for r in rows]
            )
        else:
            self._idx_ids = []
            self._idx_vecs = np.empty((0, 384), dtype=np.float32)

    def _init_tables(self):
        self._database.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id      INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                vector  BLOB
            );
        """)

    def _embed(self, text: str) -> np.ndarray:
        return next(self._embedder.embed(text))

    def retrieve(self, query: str, top_k: int = MEMORY_RETRIEVE_TOP_K) -> str:
        if not len(self._idx_vecs):
            return ""

        query_vec = self._embed(query)
        scores = self._idx_vecs @ query_vec
        indices = np.argsort(-scores)
        indices = [i for i in indices if scores[i] >= 0.55][:top_k]
        if not indices:
            return ""
        rowids = [self._idx_ids[i] for i in indices]

        placeholders = ",".join("?" for _ in rowids)
        memories = self._database.execute(
            f"SELECT content FROM memories "
            f"WHERE id IN ({placeholders})",
            rowids,
        ).fetchall()

        return "\n".join(f"- {r[0]}" for r in memories)

    def store(self, user_input: str):
        if len(user_input) < 20 or user_input.strip().endswith('?'):
            return

        vec = self._embed(user_input)

        cur = self._database.execute(
            "INSERT INTO memories (content, vector) VALUES (?, ?)",
            (user_input, vec.tobytes()),
        )
        self._idx_ids.append(cur.lastrowid)
        self._idx_vecs = np.vstack([self._idx_vecs, vec])
        self._database.commit()

