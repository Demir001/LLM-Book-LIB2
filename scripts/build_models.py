# scripts/build_models.py
"""
build_models.py
---------------------------------------
Bu script, tüm model repolarını indirip cache dizinine hazırlar.
Paralel GPU/CPU yüklemeyi yönetir ve model indirme/sıcak başlatma işlemlerini yapar.
"""

import os
import asyncio
import torch
from transformers import AutoModel, AutoTokenizer
from concurrent.futures import ThreadPoolExecutor
from backend.config import Config

# ==========================
# MODEL BİLGİLERİ
# ==========================
MODEL_LIST = [
    {"name": "embedding", "repo": Config.EMBEDDING_MODEL_REPO},
    {"name": "reranker", "repo": Config.RERANKER_MODEL_REPO},
    {"name": "llm", "repo": Config.LLM_MODEL_REPO},
]

# ==========================
# ASENKRON İNDİRME
# ==========================
async def download_model(model_info: dict):
    """Modeli indirir ve cache dizinine yükler."""
    name = model_info["name"]
    repo = model_info["repo"]
    print(f"[{name}] {repo} indiriliyor...")

    loop = asyncio.get_event_loop()
    def _load_model():
        # tokenizer ve model yükleme (HF Transformers)
        tokenizer = AutoTokenizer.from_pretrained(repo, cache_dir=Config.MODEL_CACHE_DIR)
        model = AutoModel.from_pretrained(repo, cache_dir=Config.MODEL_CACHE_DIR)
        return tokenizer, model

    try:
        tokenizer, model = await loop.run_in_executor(None, _load_model)
        print(f"[{name}] Başarıyla indirildi ve cache'e alındı: {Config.MODEL_CACHE_DIR}")
    except Exception as e:
        print(f"[{name}] Model yüklenirken hata oluştu:", e)

async def build_all_models():
    """Tüm modelleri paralel indirir ve hazırlar."""
    tasks = []
    for m in MODEL_LIST:
        tasks.append(download_model(m))
    await asyncio.gather(*tasks)

# ==========================
# GPU DURUMU
# ==========================
def show_device_info():
    if torch.cuda.is_available():
        print(f"CUDA cihazları: {torch.cuda.device_count()} GPU")
        for i in range(torch.cuda.device_count()):
            name = torch.cuda.get_device_name(i)
            mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            print(f" - GPU {i}: {name} ({mem:.1f} GB)")
    else:
        print("CUDA bulunamadı, CPU üzerinde çalışacak.")

# ==========================
# ANA FONKSİYON
# ==========================
def main():
    print("=== Model Build / Warmup Script ===")
    show_device_info()
    Config.ensure_directories()
    print(f"Cache dizini: {Config.MODEL_CACHE_DIR}")
    print("Modeller paralel olarak indirilecek...")

    asyncio.run(build_all_models())
    print("Tüm modeller indirildi ve hazır.")

# ==========================
# DOĞRUDAN ÇALIŞTIRMA
# ==========================
if __name__ == "__main__":
    main()
