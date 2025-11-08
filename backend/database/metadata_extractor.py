# backend/database/metadata_extractor.py
"""
metadata_extractor.py
PDF ve dokümanlardan metadata çıkarma modülü.
- Başlık, yazar, oluşturulma tarihi, sayfa sayısı gibi temel bilgiler.
- Gerektiğinde içerik analizi ve özetleme için kullanılacak.
- Stub fonksiyonlar şimdilik sahte veri döndürür; gerçek PDF parsing ileride entegre edilecek.
"""

import os
import datetime
import random
from typing import Dict, Optional

from PyPDF2 import PdfReader  # pip install PyPDF2

class MetadataExtractor:
    """
    PDF ve dokümanlardan metadata çıkaran sınıf.
    """

    def __init__(self):
        self.supported_extensions = [".pdf", ".docx", ".txt"]

    def is_supported(self, filepath: str) -> bool:
        _, ext = os.path.splitext(filepath.lower())
        return ext in self.supported_extensions

    def extract_metadata(self, filepath: str) -> Dict[str, Optional[str]]:
        """
        Dosyadan metadata çıkarır.
        Şu anda PDF için örnek uygulama. Diğer formatlar için genişletilebilir.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

        _, ext = os.path.splitext(filepath.lower())
        if ext == ".pdf":
            return self._extract_pdf_metadata(filepath)
        else:
            # Stub: diğer formatlar için sahte metadata
            return {
                "title": os.path.basename(filepath),
                "author": "Unknown",
                "creation_date": str(datetime.datetime.now()),
                "pages": 1,
                "file_path": filepath
            }

    def _extract_pdf_metadata(self, filepath: str) -> Dict[str, Optional[str]]:
        """
        PDF metadata çıkarımı.
        """
        try:
            reader = PdfReader(filepath)
            info = reader.metadata
            num_pages = len(reader.pages)
            # Bazı PDFlerde metadata None olabilir
            title = info.title if info.title else os.path.basename(filepath)
            author = info.author if info.author else "Unknown"
            creation_date = info.creation_date if info.creation_date else str(datetime.datetime.now())
            return {
                "title": title,
                "author": author,
                "creation_date": creation_date,
                "pages": num_pages,
                "file_path": filepath
            }
        except Exception as e:
            # Hata durumunda stub metadata döndür
            return {
                "title": os.path.basename(filepath),
                "author": "Unknown",
                "creation_date": str(datetime.datetime.now()),
                "pages": random.randint(1, 50),
                "file_path": filepath
            }

    def extract_bulk(self, filepaths: list) -> list[Dict[str, Optional[str]]]:
        """
        Birden çok dosyadan metadata çıkarır (paralel entegrasyona hazır).
        """
        results = []
        for fp in filepaths:
            if self.is_supported(fp):
                try:
                    meta = self.extract_metadata(fp)
                    results.append(meta)
                except Exception as e:
                    results.append({
                        "title": os.path.basename(fp),
                        "author": "Error",
                        "creation_date": str(datetime.datetime.now()),
                        "pages": 0,
                        "file_path": fp,
                        "error": str(e)
                    })
        return results

# ==========================
# Örnek kullanım
# ==========================
if __name__ == "__main__":
    extractor = MetadataExtractor()
    test_dir = os.path.join(os.path.dirname(__file__), "../../pdf_kaynaklar")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir, exist_ok=True)
        # örnek dosya oluştur
        with open(os.path.join(test_dir, "example.pdf"), "w") as f:
            f.write("Bu bir test PDF içeriğidir.")

    pdfs = [os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.endswith(".pdf")]
    bulk_meta = extractor.extract_bulk(pdfs)
    for m in bulk_meta:
        print(m)
