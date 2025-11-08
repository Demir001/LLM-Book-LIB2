# backend/gpu/gpu_manager.py
"""
GPU Manager
Bu modül sistemdeki GPU ve CPU kaynaklarını tespit eder, durumlarını raporlar,
ve paralel görevler için en uygun cihazları belirler.
"""

import torch
import subprocess
from typing import List, Optional


class GPUManager:
    def __init__(self):
        self.num_gpus: int = torch.cuda.device_count()
        self.available: bool = self.num_gpus > 0
        self.device_list: List[str] = self._init_device_list()

    def _init_device_list(self) -> List[str]:
        """Cihaz listesini hazırlar: cuda:0..N veya cpu"""
        if self.available:
            return [f"cuda:{i}" for i in range(self.num_gpus)]
        else:
            return ["cpu"]

    def get_best_gpu(self) -> str:
        """
        En az kullanılan GPU'yu döndürür.
        Eğer GPU yoksa 'cpu' döner.
        """
        if not self.available:
            return "cpu"
        try:
            result = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
                encoding="utf-8"
            ).strip().split("\n")
            usage = [int(x) for x in result if x.strip()]
            best_index = usage.index(min(usage))
            return f"cuda:{best_index}"
        except Exception:
            return "cuda:0"

    def get_all_devices(self) -> List[str]:
        """Tüm cihazların listesini döndürür"""
        return self.device_list

    def show_status(self):
        """GPU/CPU durumunu konsola yazdırır"""
        print("\n=== GPU/CPU DURUMU ===")
        if not self.available:
            print("⚠️ GPU bulunamadı. Sistem CPU modunda çalışacak.")
            return
        for i in range(self.num_gpus):
            name = torch.cuda.get_device_name(i)
            total_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            cap = torch.cuda.get_device_properties(i).major, torch.cuda.get_device_properties(i).minor
            print(f"GPU {i}: {name} | {total_mem:.2f} GB | Compute Capability: {cap}")
        print("======================\n")

    def device_summary(self) -> str:
        """GPU/CPU özetini string olarak döndürür"""
        if self.available:
            lines = []
            for i in range(self.num_gpus):
                name = torch.cuda.get_device_name(i)
                mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                lines.append(f"[GPU {i}] {name} ({mem:.1f} GB)")
            return "\n".join(lines)
        else:
            return "CPU Mode (CUDA not available)"

    def select_device_for_task(self, task_index: int) -> str:
        """Round-robin veya basit atama ile cihaz seçer"""
        if not self.available:
            return "cpu"
        return self.device_list[task_index % self.num_gpus]

    def is_cuda_available(self) -> bool:
        return self.available

    def num_available_gpus(self) -> int:
        return self.num_gpus

    def get_device_by_index(self, index: int) -> str:
        if not self.available:
            return "cpu"
        return self.device_list[index % self.num_gpus]


# ==========================
# Test & Demo
# ==========================
if __name__ == "__main__":
    manager = GPUManager()
    manager.show_status()
    print("En uygun GPU:", manager.get_best_gpu())
    print("Tüm cihazlar:", manager.get_all_devices())
    print("Round-robin seçimi (5 görev):")
    for i in range(5):
        print(f"TASK {i}: {manager.select_device_for_task(i)}")
