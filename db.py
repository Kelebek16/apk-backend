import psycopg
from config import Config


def get_conn():
    return psycopg.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
    )


def put_conn(conn):
    if conn is not None:
        conn.close()
