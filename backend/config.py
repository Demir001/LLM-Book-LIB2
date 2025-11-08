# backend/config.py
"""
Config.py
Tam entegre sistem yapılandırma modülü.
Bu modül GPU yönetimi, model yolları, RAG parametreleri, frontend/backend ayarları ve sistem modlarını tanımlar.
Tüm alt modüller Config sınıfı üzerinden global olarak erişir.
"""

import os
import torch
import multiprocessing
import platform
import socket
from datetime import datetime


class Config:
    # ==========================
    # GENEL SİSTEM AYARLARI
    # ==========================
    APP_NAME: str = "Advanced RAG System"
    VERSION: str = "v5.0.0"
    AUTHOR: str = "autonomous-ai"
    CREATED_AT: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    PYTHON_VERSION: str = platform.python_version()
    HOSTNAME: str = socket.gethostname()

    # ==========================
    # DİZİN YAPISI
    # ==========================
    ROOT_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    BACKEND_DIR: str = os.path.join(ROOT_DIR, "backend")
    FRONTEND_DIR: str = os.path.join(ROOT_DIR, "frontend")
    MODEL_CACHE_DIR: str = os.path.join(ROOT_DIR, "models")
    QDRANT_PATH: str = os.path.join(ROOT_DIR, "qdrant_data")
    LOG_DIR: str = os.path.join(ROOT_DIR, "logs")
    PDF_SOURCE_DIR: str = os.path.join(ROOT_DIR, "pdf_kaynaklar")
    PROCESSED_LOG_FILE: str = os.path.join(LOG_DIR, "processed_files.log")

    # ==========================
    # GPU / CİHAZ AYARLARI
    # ==========================
    NUM_GPUS: int = torch.cuda.device_count()
    CPU_COUNT: int = multiprocessing.cpu_count()
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    USE_MPS: bool = torch.backends.mps.is_available() if hasattr(torch.backends, "mps") else False
    GPU_MEMORY_UTILIZATION: float = 0.9
    TENSOR_PARALLEL_SIZE: int = max(1, NUM_GPUS)
    PER_DEVICE_CONCURRENCY: int = 2
    THREAD_POOL_WORKERS: int = max(4, CPU_COUNT // 2)

    # ==========================
    # MODEL AYARLARI
    # ==========================
    EMBEDDING_MODEL_REPO: str = "sentence-transformers/all-mpnet-base-v2"
    RERANKER_MODEL_REPO: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    LLM_MODEL_REPO: str = "cpatonn/Qwen3-Next-80B-A3B-Instruct-AWQ-4bit"
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    LLM_CONTEXT_SIZE: int = 8192
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_NEW_TOKENS: int = 1024
    ENABLE_QUERY_EXPANSION: bool = True
    ENABLE_HYDE: bool = True

    # ==========================
    # RETRIEVAL & CHUNK AYARLARI
    # ==========================
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    RETRIEVAL_TOP_K_CANDIDATES: int = 50
    RETRIEVAL_FINAL_TOP_K: int = 7
    MAX_INGEST_CONCURRENCY: int = 4

    # ==========================
    # QDRANT / VERİTABANI
    # ==========================
    QDRANT_COLLECTION_NAME: str = "kurumsal_kutuphane_v5"
    QDRANT_DISTANCE_METRIC: str = "COSINE"
    QDRANT_BATCH_SIZE: int = 128
    QDRANT_TIMEOUT: int = 60

    # ==========================
    # MODLAR
    # ==========================
    AVAILABLE_MODES = ["console", "api", "full"]
    MODE: str = "console"

    # ==========================
    # FRONTEND / API
    # ==========================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_PORT: int = 5173
    ENABLE_CORS: bool = True
    ENABLE_WEBSOCKET: bool = True

    # ==========================
    # LOGGING / DEBUG
    # ==========================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.path.join(LOG_DIR, "system.log")
    ENABLE_COLOR_LOGS: bool = True
    ENABLE_FILE_LOGGING: bool = True
    SHOW_CONFIG_ON_START: bool = True
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

    # ==========================
    # TEST / SIMULATION
    # ==========================
    SIMULATION_MODE: bool = False
    SIMULATED_LATENCY_RANGE = (0.2, 1.5)

    # ==========================
    # UTİL FONKSİYONLAR
    # ==========================
    @staticmethod
    def ensure_directories():
        """Gerekli dizinleri oluşturur."""
        for path in [
            Config.MODEL_CACHE_DIR,
            Config.QDRANT_PATH,
            Config.LOG_DIR,
            Config.PDF_SOURCE_DIR,
        ]:
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def show_summary():
        """Sistem konfigürasyon özetini yazdırır."""
        print("\n" + "=" * 70)
        print(f"{Config.APP_NAME} ({Config.VERSION})".center(70))
        print("=" * 70)
        print(f"🧠  Cihaz Türü     : {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        print(f"🎮  GPU Sayısı     : {Config.NUM_GPUS}")
        print(f"🔩  Paralel Tensor : {Config.TENSOR_PARALLEL_SIZE}")
        print(f"💾  Model Cache    : {Config.MODEL_CACHE_DIR}")
        print(f"📦  Koleksiyon     : {Config.QDRANT_COLLECTION_NAME}")
        print(f"🌍  API Portu      : {Config.API_PORT}")
        print(f"💬  Frontend Portu : {Config.FRONTEND_PORT}")
        print(f"🧩  Mod            : {Config.MODE}")
        print(f"🔍  Query Expand   : {Config.ENABLE_QUERY_EXPANSION}")
        print(f"🧠  HyDE           : {Config.ENABLE_HYDE}")
        print(f"🧱  CPU Thread Sayısı: {Config.CPU_COUNT}")
        print(f"🐍  Python Versiyonu : {Config.PYTHON_VERSION}")
        print("=" * 70 + "\n")

    @staticmethod
    def device_summary() -> str:
        """Cihaz özetini metin olarak döndürür."""
        lines = []
        if torch.cuda.is_available():
            for i in range(Config.NUM_GPUS):
                name = torch.cuda.get_device_name(i)
                cap = torch.cuda.get_device_capability(i)
                total_mem = round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2)
                lines.append(f"[GPU {i}] {name} ({total_mem} GB, Compute {cap})")
        else:
            lines.append("CPU Mode (CUDA not available)")
        return "\n".join(lines)

    @staticmethod
    def print_device_summary():
        """GPU/CPU cihaz detaylarını yazdırır."""
        print("\n--- Cihaz Detayları ---")
        print(Config.device_summary())
        print("------------------------\n")

    @staticmethod
    def as_dict() -> dict:
        """Config'i JSON olarak döndürür."""
        return {
            "app_name": Config.APP_NAME,
            "version": Config.VERSION,
            "device": Config.DEVICE,
            "num_gpus": Config.NUM_GPUS,
            "cpu_count": Config.CPU_COUNT,
            "tensor_parallel_size": Config.TENSOR_PARALLEL_SIZE,
            "gpu_memory_utilization": Config.GPU_MEMORY_UTILIZATION,
            "embedding_model": Config.EMBEDDING_MODEL_REPO,
            "llm_model": Config.LLM_MODEL_REPO,
            "reranker_model": Config.RERANKER_MODEL_REPO,
            "retrieval_top_k": Config.RETRIEVAL_TOP_K_CANDIDATES,
            "retrieval_final_top_k": Config.RETRIEVAL_FINAL_TOP_K,
            "api_port": Config.API_PORT,
            "frontend_port": Config.FRONTEND_PORT,
            "mode": Config.MODE,
        }

    @staticmethod
    def validate():
        """Kritik yapılandırma doğrulamaları."""
        assert Config.EMBEDDING_MODEL_REPO, "Embedding modeli tanımlanmadı!"
        assert Config.LLM_MODEL_REPO, "LLM modeli tanımlanmadı!"
        assert Config.QDRANT_COLLECTION_NAME, "Qdrant koleksiyon adı eksik!"
        if Config.MODE not in Config.AVAILABLE_MODES:
            raise ValueError(f"Geçersiz çalışma modu: {Config.MODE}")
        if not (0 < Config.GPU_MEMORY_UTILIZATION <= 1):
            raise ValueError("GPU_MEMORY_UTILIZATION 0 ile 1 arasında olmalı!")
        if Config.RETRIEVAL_FINAL_TOP_K > Config.RETRIEVAL_TOP_K_CANDIDATES:
            raise ValueError("RETRIEVAL_FINAL_TOP_K, RETRIEVAL_TOP_K_CANDIDATES'tan büyük olamaz!")

    @staticmethod
    def env_info():
        """Sistem bilgilerini döndürür."""
        import platform, sys
        return {
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "interpreter": sys.executable,
        }


# ==========================
# MODÜL YÜKLENİRKEN
# ==========================
if __name__ == "__main__":
    Config.ensure_directories()
    Config.validate()
    Config.show_summary()
    Config.print_device_summary()
    print("Yapılandırma başarıyla doğrulandı.")
