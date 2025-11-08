# backend/gpu/device_allocator.py
"""
Device Allocator
----------------
GPU/CPU cihazlarının yönetimi ve görev ataması için modül.
- Çoklu GPU ortamında round-robin veya yük bazlı dağıtım sağlar.
- Task başına cihaz seçimi ve concurrency kontrolü sağlar.
- Paralel RAG / PDF ingestion işlemlerinde kullanılmak üzere tasarlanmıştır.
"""

import asyncio
import torch
from typing import List, Optional, Dict
import itertools

class DeviceAllocator:
    """
    Çoklu GPU / CPU ortamı için cihaz atama ve concurrency yönetimi.
    """
    def __init__(self, devices: Optional[List[str]] = None, per_device_concurrency: int = 2):
        # Kullanılacak cihaz listesi
        if devices is None:
            if torch.cuda.is_available():
                self.devices = [f"cuda:{i}" for i in range(torch.cuda.device_count())]
            else:
                self.devices = ["cpu"]
        else:
            self.devices = devices

        # Her cihaz için semaphore (aynı anda max görev)
        self.device_semaphores: Dict[str, asyncio.Semaphore] = {
            device: asyncio.Semaphore(per_device_concurrency) for device in self.devices
        }

        # Round-robin iterator
        self._device_cycle = itertools.cycle(self.devices)

    def get_next_device(self) -> str:
        """Round-robin ile sıradaki cihazı döndürür."""
        return next(self._device_cycle)

    def all_devices(self) -> List[str]:
        """Cihaz listesini döndürür."""
        return self.devices

    async def acquire(self, device: str) -> None:
        """Semaphore kilidi alır (görev başlatmadan önce)."""
        sem = self.device_semaphores.get(device)
        if sem is not None:
            await sem.acquire()

    def release(self, device: str) -> None:
        """Semaphore kilidini serbest bırakır (görev bitince)."""
        sem = self.device_semaphores.get(device)
        if sem is not None:
            sem.release()

    async def run_on_device(self, device: str, coro_func, *args, **kwargs):
        """
        Coroutine fonksiyonunu belirtilen cihazda çalıştırır.
        Otomatik semaphore kontrolü sağlar.
        """
        await self.acquire(device)
        try:
            if asyncio.iscoroutinefunction(coro_func):
                return await coro_func(*args, device=device, **kwargs)
            else:
                # Normal fonksiyon ise thread pool kullan
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: coro_func(*args, device=device, **kwargs))
        finally:
            self.release(device)

    async def run_round_robin(self, coro_func, *args, **kwargs):
        """
        Round-robin cihaz ataması ile coroutine çalıştırır.
        """
        device = self.get_next_device()
        return await self.run_on_device(device, coro_func, *args, **kwargs)

    def status(self) -> str:
        """Cihaz ve semaphore durum özetini döndürür."""
        lines = []
        for d, sem in self.device_semaphores.items():
            lines.append(f"[{d}] Active Tasks: {sem._value}/{sem._initial_value}")
        return "\n".join(lines)


# ==========================
# Örnek kullanım / test
# ==========================
if __name__ == "__main__":
    import random

    async def dummy_task(name, device="cpu"):
        print(f"[{device}] Task {name} başladı.")
        await asyncio.sleep(random.uniform(0.5, 1.5))
        print(f"[{device}] Task {name} bitti.")
        return f"{name} done"

    async def main():
        allocator = DeviceAllocator(per_device_concurrency=2)
        tasks = [allocator.run_round_robin(dummy_task, f"task-{i}") for i in range(6)]
        results = await asyncio.gather(*tasks)
        print("Sonuçlar:", results)
        print(allocator.status())

    asyncio.run(main())
