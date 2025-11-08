# backend/main.py
"""
Main.py
Sistem başlatıcı dosyası.
- Console / API / Full modları destekler.
- GPU/CPU cihazlarını otomatik tespit eder.
- Paralel Executor ile görevleri yönetir.
"""

import argparse
import asyncio
import sys

from backend.config import Config
from backend.gpu.gpu_manager import GPUManager

def parse_args():
    parser = argparse.ArgumentParser(description="Advanced RAG System Launcher")
    parser.add_argument(
        "--mode",
        choices=Config.AVAILABLE_MODES,
        default=Config.MODE,
        help="Çalışma modu: console | api | full"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug modu aktif eder"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    Config.MODE = args.mode
    Config.DEBUG_MODE = args.debug

    # GPU durumu
    gpu_manager = GPUManager()
    gpu_manager.show_status()

    # Config özeti
    Config.show_summary()

    # Mode seçimine göre başlat
    if args.mode == "console":
        from backend.console_runner import start_console_mode
        asyncio.run(start_console_mode())
    elif args.mode == "api":
        from backend.app import start_api_mode
        asyncio.run(start_api_mode())
    elif args.mode == "full":
        from backend.startup import start_full_stack
        asyncio.run(start_full_stack())
    else:
        print(f"Geçersiz mod: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
