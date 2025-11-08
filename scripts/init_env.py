# scripts/init_env.py
"""
init_env.py
Proje başlangıç ortamını hazırlar:
- Gerekli dizinleri oluşturur
- Sanal ortam veya paketleri kontrol eder
- Örnek PDF ve log dizinlerini hazırlar
- İlk Qdrant koleksiyonunu oluşturur (stub)
"""

import os
import sys
import subprocess
from pathlib import Path

# -----------------------------
# Dizini ve temel yolları ayarla
# -----------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
PDF_DIR = ROOT_DIR / "pdf_kaynaklar"
LOG_DIR = ROOT_DIR / "logs"
MODEL_DIR = ROOT_DIR / "models"
QDRANT_DIR = ROOT_DIR / "qdrant_data"

DIRS = [PDF_DIR, LOG_DIR, MODEL_DIR, QDRANT_DIR]

# -----------------------------
# Dizinleri oluştur
# -----------------------------
for d in DIRS:
    d.mkdir(parents=True, exist_ok=True)
    print(f"[✔] Dizin hazır: {d}")

# -----------------------------
# Örnek PDF dosyaları ekle
# -----------------------------
sample_pdfs = ["test1.pdf", "test2.pdf", "sample_doc.pdf"]
for f in sample_pdfs:
    path = PDF_DIR / f
    if not path.exists():
        with open(path, "w", encoding="utf-8") as file:
            file.write(f"Bu bir örnek PDF içeriğidir: {f}")
        print(f"[✔] Örnek PDF oluşturuldu: {path}")
    else:
        print(f"[ℹ] Örnek PDF zaten mevcut: {path}")

# -----------------------------
# Qdrant (stub) başlat / kontrol
# -----------------------------
try:
    import qdrant_client
    print("[✔] Qdrant kütüphanesi yüklü.")
except ImportError:
    print("[⚠] Qdrant yüklü değil. Yüklemek için:")
    print("      pip install qdrant-client")
    # opsiyonel olarak yükleyebiliriz
    # subprocess.run([sys.executable, "-m", "pip", "install", "qdrant-client"], check=True)

# -----------------------------
# Sanal ortam ve paket kontrolü
# -----------------------------
try:
    import torch
    import fastapi
    print("[✔] Temel Python paketleri yüklü.")
except ImportError as e:
    print(f"[⚠] Paket eksik: {e.name}. Yüklemek için:")
    print(f"      pip install {e.name}")

# -----------------------------
# Başlatma mesajı
# -----------------------------
print("\n[🎉] Ortam başlatıldı ve test dizinleri hazır!")
print("PDF dizini:", PDF_DIR)
print("Log dizini:", LOG_DIR)
print("Model dizini:", MODEL_DIR)
print("Qdrant dizini:", QDRANT_DIR)
print("\nArtık 'backend/main.py --mode console' ile sistemi çalıştırabilirsiniz.")
