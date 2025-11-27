
import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5433))
    DB_NAME = os.getenv("DB_NAME", "labeling_db")
    DB_USER = os.getenv("DB_USER", "emre")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    SECRET_KEY = os.getenv("SECRET_KEY", "change_me_please")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5433),
    "database": os.getenv("DB_NAME", "labeling_db"),
    "user": os.getenv("DB_USER", "emre"),
    "password": os.getenv("DB_PASSWORD")
}
