# backend/database/qdrant_manager.py
"""
qdrant_manager.py
Qdrant vektör veritabanı yönetimi için tam entegre modül.
- Koleksiyon oluşturma, silme, indeksleme
- Vektör ekleme / sorgulama
- Batch işlemleri ve paralel ingestion
- Çoklu cihaz ve concurrency desteği
"""

import os
import asyncio
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from backend.config import Config
from backend.gpu.parallel_executor import ParallelExecutor


class QdrantManager:
    def __init__(self, host: str = "127.0.0.1", port: int = 6333):
        self.host = host
        self.port = port
        self.collection_name = Config.QDRANT_COLLECTION_NAME
        self.client = QdrantClient(host=self.host, port=self.port)
        self._executor: Optional[ParallelExecutor] = None

    def set_executor(self, executor: ParallelExecutor):
        """Paralel görev dağıtıcıyı ata."""
        self._executor = executor

    def ensure_collection(self):
        """Koleksiyon var mı kontrol et, yoksa oluştur."""
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]
        if self.collection_name in names:
            print(f"Koleksiyon zaten var: {self.collection_name}")
        else:
            print(f"Koleksiyon oluşturuluyor: {self.collection_name}")
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=768,  # embedding boyutu, modelden alınmalı
                    distance=Distance.COSINE,
                )
            )

    async def add_vectors_async(self, vectors: List[Dict[str, Any]], batch_size: int = Config.QDRANT_BATCH_SIZE):
        """Vektörleri batch olarak ekle (async)."""
        if not self._executor:
            raise RuntimeError("ParallelExecutor ayarlanmamış!")
        tasks = []
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            tasks.append(self._executor.submit(self._add_batch, batch))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def _add_batch(self, batch: List[Dict[str, Any]]):
        """Batch vektör ekleme (senkron, executor tarafından çağrılır)."""
        try:
            points = [{"id": v.get("id"), "vector": v.get("embedding"), "payload": v.get("metadata", {})} for v in batch]
            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"Batch eklendi: {len(batch)} vektör")
            return len(batch)
        except Exception as e:
            print("Batch eklenirken hata:", e)
            return e

    def query(self, vector: List[float], top_k: int = Config.RETRIEVAL_TOP_K_CANDIDATES):
        """Tek bir vektör ile sorgu yap."""
        try:
            response = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=top_k,
            )
            return response
        except Exception as e:
            print("Sorgu hatası:", e)
            return []

    def delete_collection(self):
        """Koleksiyonu tamamen sil."""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Koleksiyon silindi: {self.collection_name}")
        except Exception as e:
            print("Koleksiyon silme hatası:", e)

    def collection_info(self):
        """Koleksiyon hakkında bilgi döndürür."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info
        except Exception as e:
            print("Koleksiyon bilgisi alınamadı:", e)
            return {}

    async def ingest_embeddings_parallel(self, embeddings: List[Dict[str, Any]]):
        """Embeddingleri executor ile paralel ekle."""
        if not self._executor:
            raise RuntimeError("ParallelExecutor ayarlanmamış!")
        batch_size = Config.QDRANT_BATCH_SIZE
        tasks = []
        for i in range(0, len(embeddings), batch_size):
            batch = embeddings[i:i+batch_size]
            tasks.append(self._executor.submit(self._add_batch, batch))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in results if not isinstance(r, Exception))
        print(f"İşlem tamamlandı. Başarılı batch sayısı: {success}/{len(tasks)}")
        return results


# ==========================
# KOLAY TEST
# ==========================
if __name__ == "__main__":
    import random

    # Dummy executor
    from backend.gpu.parallel_executor import ParallelExecutor
    executor = ParallelExecutor(devices=["cpu"], per_device_concurrency=2)

    qm = QdrantManager()
    qm.set_executor(executor)
    qm.ensure_collection()

    # 5 adet sahte vektör ekleme
    dummy_vectors = [{"id": f"vec{i}", "embedding": [random.random() for _ in range(768)], "metadata": {"name": f"doc{i}"}} for i in range(5)]

    async def test_ingest():
        await qm.ingest_embeddings_parallel(dummy_vectors)
        info = qm.collection_info()
        print("Koleksiyon bilgisi (özeti):", info)

    asyncio.run(test_ingest())
