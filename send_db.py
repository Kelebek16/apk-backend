import os
import psycopg
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

POSITIVE_FILE = "pozitif_cleaned.txt"
NEGATIVE_FILE = "negatif_cleaned.txt"
DATA_FILE = "output_unique.txt"

BATCH_SIZE = 1000


def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def read_txt(path):
    if not os.path.exists(path):
        print(f"⚠️ Dosya bulunamadı: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def chunked(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]


def insert_data_txt(conn, lines):
    print(f"\n📥 {DATA_FILE} → tweets_queue ({len(lines)} satır)")
    now = datetime.now(timezone.utc)

    sql = """
    INSERT INTO tweets_queue (tweet_text, is_processed, created_at)
    SELECT unnest(%s::text[]), FALSE, %s
    """

    with conn.cursor() as cur:
        for batch in chunked(lines, BATCH_SIZE):
            cur.execute(sql, (batch, now))
        conn.commit()

    print("✅ data.txt yüklendi")


def insert_labeled(conn, lines, label):
    target_table = "positive" if label == "positive" else "negative"
    print(f"\n📥 {label.upper()} → tweets_queue + {target_table} ({len(lines)} satır)")
    now = datetime.now(timezone.utc)

    insert_queue_sql = """
    INSERT INTO tweets_queue (tweet_text, is_processed, label, processed_at)
    SELECT unnest(%s::text[]), TRUE, %s, %s
    RETURNING id, tweet_text
    """

    insert_child_sql = f"""
    INSERT INTO {target_table} (data_id, tweet_text)
    VALUES (%s, %s)
    """

    with conn.cursor() as cur:
        for batch in chunked(lines, BATCH_SIZE):
            cur.execute(insert_queue_sql, (batch, label, now))
            rows = cur.fetchall()

            cur.executemany(
                insert_child_sql,
                [(row[0], row[1]) for row in rows]
            )

        conn.commit()

    print(f"✅ {label} verileri yüklendi")


def main():
    print("🚀 TXT yükleme başlıyor...")

    conn = get_conn()

    try:
        data_lines = read_txt(DATA_FILE)
        positive_lines = read_txt(POSITIVE_FILE)
        negative_lines = read_txt(NEGATIVE_FILE)

        if data_lines:
            insert_data_txt(conn, data_lines)

        if positive_lines:
            insert_labeled(conn, positive_lines, "positive")

        if negative_lines:
            insert_labeled(conn, negative_lines, "negative")

        print("\n🎉 TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI")

    except Exception as e:
        conn.rollback()
        print(f"❌ HATA: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
