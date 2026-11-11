import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

nivel = os.getenv("LOG_LEVEL", "INFO")
archivo = Path(__file__).resolve().parents[2] / os.getenv("LOG_FILE", "logs/api.log")
archivo.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("contentflow")
logger.setLevel(nivel)

if not logger.handlers:
    formato = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    a_archivo = logging.FileHandler(archivo, encoding="utf-8")
    a_archivo.setFormatter(formato)

    a_consola = logging.StreamHandler()
    a_consola.setFormatter(formato)

    logger.addHandler(a_archivo)
    logger.addHandler(a_consola)