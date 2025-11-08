# backend/database/pdf_ingestor.py
"""
PDF Ingestor Modülü
-------------------
Bu modül, PDF dosyalarını okuyup sayfa sayfa ayırır,
metinleri parçalara böler, embedding oluşturur ve
veritabanına ekler. Paralel çalışmayı destekler.
"""

import os
import asyncio
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from backend.config import Config
from backend.gpu.parallel_executor import ParallelExecutor

# TODO: Gerçek embedding ve Qdrant entegrasyonu için stublar hazırlandı
# from backend.llm.llm_engine import EmbeddingEngine
# from backend.database.qdrant_manager import QdrantManager

class PDFIngestor:
    """PDF ingestion pipeline."""

    def __init__(self, executor: ParallelExecutor, pdf_dir: str = None):
        self.pdf_dir = pdf_dir or Config.PDF_SOURCE_DIR
        self.executor = executor
        # self.embedding_engine = EmbeddingEngine()
        # self.qdrant = QdrantManager()

    async def ingest_all(self) -> List[Dict[str, Any]]:
        """PDF dizinindeki tüm dosyaları paralel işleme alır."""
        pdfs = [f for f in os.listdir(self.pdf_dir) if f.lower().endswith('.pdf')]
        if not pdfs:
            print("PDF bulunamadı:", self.pdf_dir)
            return []

        tasks = [self.executor.submit(self.ingest_single_pdf, os.path.join(self.pdf_dir, pdf))
                 for pdf in pdfs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def ingest_single_pdf(self, filepath: str) -> Dict[str, Any]:
        """Tek bir PDF'i sayfa sayfa ayırır ve stub embedding üretir."""
        filename = os.path.basename(filepath)
        print(f"📄 Başlıyor: {filename}")
        try:
            reader = PdfReader(filepath)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            # Sayfa başına chunk oluştur
            chunks = self.chunk_pages(pages_text)
            # Embedding hesaplama stub
            embeddings = await self.executor.submit(self.stub_embedding, chunks)
            # Qdrant insert stub
            # await self.qdrant.insert(chunks, embeddings)
            print(f"✅ Tamamlandı: {filename} ({len(chunks)} chunk)")
            return {"file": filename, "status": "success", "chunks": len(chunks)}
        except Exception as e:
            print(f"❌ Hata PDF: {filename} -> {e}")
            return {"file": filename, "status": "error", "error": str(e)}

    def chunk_pages(self, pages: List[str], chunk_size: int = Config.CHUNK_SIZE,
                    overlap: int = Config.CHUNK_OVERLAP) -> List[str]:
        """Sayfaları belirli uzunlukta parçalara böler, overlap ekler."""
        chunks = []
        for page_text in pages:
            words = page_text.split()
            i = 0
            while i < len(words):
                chunk = " ".join(words[i:i + chunk_size])
                chunks.append(chunk)
                i += chunk_size - overlap
        return chunks

    async def stub_embedding(self, chunks: List[str]) -> List[List[float]]:
        """Embedding stub (gerçek model çağrısı ile değiştirilecek)."""
        results = []
        for chunk in chunks:
            # Simüle edilmiş embedding vektörü (length=768)
            vec = [float(ord(c) % 256) / 255.0 for c in chunk[:768]]
            results.append(vec)
            await asyncio.sleep(0.001)  # minimal async simülasyon
        return results


# ==========================
# TEST / ÖRNEK
# ==========================
if __name__ == "__main__":
    import asyncio
    from backend.gpu.parallel_executor import ParallelExecutor

    executor = ParallelExecutor(devices=["cpu"], per_device_concurrency=2)
    ingestor = PDFIngestor(executor, pdf_dir=Config.PDF_SOURCE_DIR)

    async def main():
        results = await ingestor.ingest_all()
        print("İşlenen PDFler:", results)

    asyncio.run(main())
