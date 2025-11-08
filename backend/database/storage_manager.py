# backend/database/storage_manager.py
"""
storage_manager.py
Veri saklama ve dosya yönetimi modülü.
PDF, metadata ve embedding verilerini yönetir.
Qdrant, disk veya başka depolama tipleri ile entegre çalışabilir.
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from backend.config import Config


class StorageManager:
    """
    StorageManager, tüm veri dosyalarının ve meta bilgilerin düzenli bir şekilde saklanmasını sağlar.
    - PDF'ler
    - Chunk metadata
    - Embedding verileri
    """

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = root_dir or Config.ROOT_DIR
        self.pdf_dir = Path(Config.PDF_SOURCE_DIR)
        self.processed_dir = Path(os.path.join(self.root_dir, "processed_pdfs"))
        self.metadata_dir = Path(os.path.join(self.root_dir, "metadata"))
        self.embeddings_dir = Path(os.path.join(self.root_dir, "embeddings"))
        self._ensure_directories()

    def _ensure_directories(self):
        """Gerekli tüm dizinleri oluşturur."""
        for d in [self.pdf_dir, self.processed_dir, self.metadata_dir, self.embeddings_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # ==========================
    # PDF DOSYALARI
    # ==========================
    def list_pdfs(self) -> List[Path]:
        """PDF dizinindeki tüm PDF dosyalarını listeler."""
        return [f for f in self.pdf_dir.glob("*.pdf") if f.is_file()]

    def move_to_processed(self, pdf_path: Path):
        """İşlenen PDF'i processed dizinine taşır."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF bulunamadı: {pdf_path}")
        dest = self.processed_dir / pdf_path.name
        shutil.move(str(pdf_path), str(dest))

    def pdf_exists(self, pdf_name: str) -> bool:
        """PDF daha önce işlenmiş mi kontrol eder."""
        processed_file = self.processed_dir / pdf_name
        return processed_file.exists()

    # ==========================
    # METADATA YÖNETİMİ
    # ==========================
    def save_metadata(self, pdf_name: str, metadata: Dict[str, Any]):
        """PDF metadata'sını JSON olarak kaydeder."""
        metadata_file = self.metadata_dir / f"{pdf_name}.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def load_metadata(self, pdf_name: str) -> Optional[Dict[str, Any]]:
        """PDF metadata'sını yükler."""
        metadata_file = self.metadata_dir / f"{pdf_name}.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_metadata_files(self) -> List[Path]:
        """Tüm metadata JSON dosyalarını listeler."""
        return [f for f in self.metadata_dir.glob("*.json") if f.is_file()]

    # ==========================
    # EMBEDDING YÖNETİMİ
    # ==========================
    def save_embedding(self, pdf_name: str, chunk_id: int, embedding: List[float]):
        """Chunk embedding verisini kaydeder."""
        emb_dir = self.embeddings_dir / pdf_name
        emb_dir.mkdir(exist_ok=True)
        emb_file = emb_dir / f"{chunk_id}.json"
        with open(emb_file, "w", encoding="utf-8") as f:
            json.dump(embedding, f)

    def load_embedding(self, pdf_name: str, chunk_id: int) -> Optional[List[float]]:
        """Chunk embedding verisini yükler."""
        emb_file = self.embeddings_dir / pdf_name / f"{chunk_id}.json"
        if emb_file.exists():
            with open(emb_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_embeddings(self, pdf_name: str) -> List[Path]:
        """Bir PDF için tüm embedding dosyalarını listeler."""
        emb_dir = self.embeddings_dir / pdf_name
        if not emb_dir.exists():
            return []
        return [f for f in emb_dir.glob("*.json") if f.is_file()]

    # ==========================
    # TEMİZLİK & BAKIM
    # ==========================
    def clear_embeddings(self, pdf_name: Optional[str] = None):
        """Embedding dizinini temizler. PDF ismi verilirse sadece o PDF'in embeddingleri silinir."""
        if pdf_name:
            emb_dir = self.embeddings_dir / pdf_name
            if emb_dir.exists():
                shutil.rmtree(emb_dir)
        else:
            shutil.rmtree(self.embeddings_dir)
            self.embeddings_dir.mkdir(parents=True, exist_ok=True)

    def clear_metadata(self, pdf_name: Optional[str] = None):
        """Metadata dizinini temizler. PDF ismi verilirse sadece o PDF'in metadata dosyası silinir."""
        if pdf_name:
            meta_file = self.metadata_dir / f"{pdf_name}.json"
            if meta_file.exists():
                meta_file.unlink()
        else:
            shutil.rmtree(self.metadata_dir)
            self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def clear_processed(self):
        """Processed PDF dizinini temizler."""
        shutil.rmtree(self.processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    # ==========================
    # GENEL YARDIMCI FONKSİYONLAR
    # ==========================
    def get_all_files_summary(self) -> Dict[str, int]:
        """PDF, metadata ve embedding sayılarıyla özet döndürür."""
        return {
            "pdf_count": len(self.list_pdfs()),
            "processed_pdf_count": len(list(self.processed_dir.glob("*.pdf"))),
            "metadata_count": len(self.list_metadata_files()),
            "embedding_count": sum(len(self.list_embeddings(f.name)) for f in self.list_pdfs()),
        }


# ==========================
# TEST / DEMO
# ==========================
if __name__ == "__main__":
    sm = StorageManager()
    print("PDF Dosyaları:", sm.list_pdfs())
    print("Metadata Dosyaları:", sm.list_metadata_files())
    print("Embeddings Dizini:", sm.embeddings_dir)
    print("Özet:", sm.get_all_files_summary())
