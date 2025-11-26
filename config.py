
import os

class Config:

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5433))
    DB_NAME = os.getenv("DB_NAME", "labeling_db")
    DB_USER = os.getenv("DB_USER", "emre")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

    SECRET_KEY = os.getenv("SECRET_KEY", "change_me_please")
