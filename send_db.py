import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATA_FILE_PATH = os.getenv("DATA_FILE_PATH", "data.txt")


def get_conn():
    """Veritabanı bağlantısı oluşturur"""
    try:
        conn = psycopg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5433),
            dbname=os.getenv('DB_NAME', 'labeling_db'),
            user=os.getenv('DB_USER', 'emre'),
            password=os.getenv('DB_PASSWORD', '96cde509439a414b528d9b3a9d8d7392')
        )
        return conn
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return None


def insert_tweets_from_file(file_path: str, batch_size: int = 1000):
    """
    data.txt içindeki satırları tweets_queue tablosuna ekler.
    Her satır = tweet_text, is_processed = FALSE
    """
    if not os.path.exists(file_path):
        print(f"❌ Dosya bulunamadı: {file_path}")
        return False

    conn = get_conn()
    if not conn:
        return False

    total_inserted = 0

    try:
        cur = conn.cursor()

        print(f"\n📂 Veri dosyası okunuyor: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            batch = []

            for line in f:
                tweet = line.strip()
                if not tweet:
                    continue

                batch.append((tweet, False))

                if len(batch) >= batch_size:
                    cur.executemany(
                        "INSERT INTO tweets_queue (tweet_text, is_processed) VALUES (%s, %s)",
                        batch
                    )
                    conn.commit()
                    total_inserted += len(batch)
                    print(f"   ➕ {total_inserted} kayıt eklendi...")
                    batch = []

            if batch:
                cur.executemany(
                    "INSERT INTO tweets_queue (tweet_text, is_processed) VALUES (%s, %s)",
                    batch
                )
                conn.commit()
                total_inserted += len(batch)

        print(f"\n✅ Toplam {total_inserted} satır tweets_queue tablosuna eklendi.")
        return True

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 data.txt verileri yükleniyor...")
    success = insert_tweets_from_file(DATA_FILE_PATH)

    if success:
        print("🎉 İşlem tamamlandı!")
    else:
        print("💥 Hata oluştu!")
