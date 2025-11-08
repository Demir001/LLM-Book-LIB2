# backend/utils/logger.py
"""
Logger.py
Gelişmiş logging modülü.
- Konsol ve dosya loglama
- Renkli loglar (opsiyonel)
- Asenkron log kuyruğu
- Farklı seviyeler: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Rotasyon destekli dosya logları
"""

import os
import sys
import logging
import logging.handlers
import threading
from datetime import datetime
from queue import Queue, Empty
from backend.config import Config


class AsyncLogger:
    LEVEL_COLORS = {
        "DEBUG": "\033[94m",    # mavi
        "INFO": "\033[92m",     # yeşil
        "WARNING": "\033[93m",  # sarı
        "ERROR": "\033[91m",    # kırmızı
        "CRITICAL": "\033[41m", # kırmızı arka plan
        "ENDC": "\033[0m",
    }

    def __init__(self, name: str = "AdvancedRAG", log_file: str = None, level: str = None):
        self.name = name
        self.level = level or Config.LOG_LEVEL.upper()
        self.log_file = log_file or Config.LOG_FILE
        self.queue = Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._logger_thread, daemon=True)
        self._setup_logger()
        self._thread.start()

    def _setup_logger(self):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.level, logging.INFO))
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

        # Dosya handler
        if Config.ENABLE_FILE_LOGGING:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Konsol handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _logger_thread(self):
        while not self._stop_event.is_set():
            try:
                record = self.queue.get(timeout=0.5)
                self._handle_record(record)
            except Empty:
                continue

    def _handle_record(self, record):
        level_name = record.get("level", "INFO").upper()
        msg = record.get("message", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if Config.ENABLE_COLOR_LOGS and level_name in self.LEVEL_COLORS:
            color = self.LEVEL_COLORS[level_name]
            endc = self.LEVEL_COLORS["ENDC"]
            msg = f"{color}{timestamp} [{level_name}] {msg}{endc}"
            print(msg)
        else:
            log_func = getattr(self.logger, level_name.lower(), self.logger.info)
            log_func(msg)

    def log(self, message: str, level: str = "INFO"):
        self.queue.put({"message": message, "level": level.upper()})

    def debug(self, message: str):
        self.log(message, "DEBUG")

    def info(self, message: str):
        self.log(message, "INFO")

    def warning(self, message: str):
        self.log(message, "WARNING")

    def error(self, message: str):
        self.log(message, "ERROR")

    def critical(self, message: str):
        self.log(message, "CRITICAL")

    def shutdown(self):
        self._stop_event.set()
        self._thread.join(timeout=2)


# ========================
# GLOBAL LOGGER ÖRNEĞİ
# ========================
logger = AsyncLogger()
if __name__ == "__main__":
    logger.info("Logger başlatıldı")
    logger.debug("Debug seviyesi testi")
    logger.warning("Uyarı testi")
    logger.error("Hata testi")
    logger.critical("Kritik hata testi")
    import time
    time.sleep(1)
    logger.shutdown()
