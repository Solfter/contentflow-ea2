import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

uri = os.getenv("MONGODB_URI")
nombre_db = os.getenv("MONGODB_DB")

if not uri or not nombre_db:
    raise RuntimeError("Faltan MONGODB_URI o MONGODB_DB en el archivo .env")

cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
db = cliente[nombre_db]