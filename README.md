# Advanced RAG System

Bu proje, PDF tabanlı içerikleri ingestion, retrieval ve LLM tabanlı cevap üretimi ile işleyen gelişmiş bir RAG sistemidir.

## Özellikler
- PDF sayfa sayfa parçalanması ve embedding
- Halüsinasyon azaltma ve doğrulama
- Paralel çalışabilir: CPU / Tek GPU / Çoklu GPU destekli
- Full stack: Backend (FastAPI) + Frontend (React)
- Console modu ile hızlı test

## Kurulum

```bash
# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Console mode (frontend olmadan test)
python backend/main.py --mode console

# API mode (sadece FastAPI backend)
python backend/main.py --mode api

# Full stack mode (backend + frontend)
python backend/main.py --mode full
