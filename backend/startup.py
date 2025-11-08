# backend/startup.py
"""
startup.py
Sistem başlangıç yönetimi modülü.
Bu modül, seçilen moda göre backend, console veya full stack başlatmayı koordine eder.
GPU ve paralel executor ayarlarını başlatır.
"""

import asyncio
import sys
from backend.config import Config
from backend.gpu.gpu_manager import GPUManager
from backend.gpu.parallel_executor import ParallelExecutor


class Startup:
    """Sistem başlatıcı sınıfı."""

    def __init__(self, mode: str = None):
        self.mode = mode or Config.MODE
        Config.MODE = self.mode
        self.gpu_manager = GPUManager()
        self.executor = ParallelExecutor(
            devices=self.gpu_manager.get_all_devices(),
            per_device_concurrency=Config.PER_DEVICE_CONCURRENCY,
            thread_pool_workers=Config.THREAD_POOL_WORKERS
        )

    def show_intro(self):
        """Başlangıçta sistem özetini yazdırır."""
        print("\n" + "="*60)
        print(f"{Config.APP_NAME} ({Config.VERSION}) - Başlatılıyor".center(60))
        print("="*60 + "\n")
        self.gpu_manager.show_status()
        Config.show_summary()

    async def _start_console_mode(self):
        """Console modunu başlatır."""
        from backend.console_runner import start_console_mode
        await start_console_mode()

    async def _start_api_mode(self):
        """API backend modunu başlatır."""
        from backend.app import start_api_mode
        await start_api_mode(self.executor)

    async def _start_full_stack_mode(self):
        """Full stack (API + Frontend) modunu başlatır."""
        from backend.app import start_api_mode
        # Frontend start işlemleri placeholder
        print("Frontend sunucusu başlatılıyor... (placeholder)")
        await start_api_mode(self.executor)
        print("Frontend başlatıldı. Tarayıcıdan erişebilirsiniz.")

    async def start(self):
        """Seçilen moda göre başlatır."""
        self.show_intro()
        if self.mode == "console":
            await self._start_console_mode()
        elif self.mode == "api":
            await self._start_api_mode()
        elif self.mode == "full":
            await self._start_full_stack_mode()
        else:
            print(f"⚠️  Geçersiz mod: {self.mode}")
            sys.exit(1)

    def run(self):
        """Senkron wrapper: asyncio event loop başlatır."""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\nÇıkış yapılıyor...")
        finally:
            print("Sistem kapanıyor...")



# ==========================
# TEST
# ==========================
if __name__ == "__main__":
    startup = Startup(mode="console")
    startup.run()
