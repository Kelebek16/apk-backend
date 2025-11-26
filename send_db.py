import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

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
        print(f"Bağlantı hatası: {e}")
        return None

def test_connection():
    """Veritabanı bağlantısını test eder"""
    conn = get_conn()
    if conn:
        conn.close()
        print("✅ Veritabanı bağlantısı başarılı!")
        return True
    return False

def check_database_status():
    """Veritabanı durumunu kontrol eder"""
    conn = get_conn()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                COUNT(*) as total_tweets,
                COUNT(CASE WHEN is_processed = TRUE THEN 1 END) as processed,
                COUNT(CASE WHEN is_processed = FALSE THEN 1 END) as unprocessed,
                COUNT(CASE WHEN label = 'positive' THEN 1 END) as positive,
                COUNT(CASE WHEN label = 'negative' THEN 1 END) as negative
            FROM tweets_queue
        """)
        stats = cur.fetchone()
        print("\n📊 VERİTABANI DURUM RAPORU:")
        print(f"   Toplam Tweet: {stats[0]}")
        print(f"   İşlenmiş: {stats[1]}")
        print(f"   İşlenmemiş: {stats[2]}")
        print(f"   Positive: {stats[3]}")
        print(f"   Negative: {stats[4]}")
        return True
    except Exception as e:
        print(f"❌ Durum kontrol hatası: {e}")
        return False
    finally:
        conn.close()

def insert_sample_tweets():
    """Örnek tweet verilerini tweets_queue tablosuna ekler"""
    conn = get_conn()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        sample_tweets = [
            ('Bugün hava gerçekten çok güzel, insanın içi neşe doluyor ☀️', False),
            ('Bu filmi izlemek hayatımın en büyük hatasıydı, çok sıkıcıydı 😫', False),
            ('Yeni aldığım telefon mükemmel çalışıyor, kesinlikle tavsiye ederim! 📱', False),
            ('Restoran berbatdı, yemekler soğuk ve servis çok yavaştı 👎', False),
            ('Arkadaşlarla harika bir akşam geçirdik, her şey mükemmeldi 🎉', False),
        ]
        
        cur.executemany(
            "INSERT INTO tweets_queue (tweet_text, is_processed) VALUES (%s, %s)",
            sample_tweets
        )
        conn.commit()
        
        cur.execute("SELECT COUNT(*) FROM tweets_queue WHERE is_processed = FALSE")
        count = cur.fetchone()[0]
        print(f"✅ {len(sample_tweets)} adet tweet başarıyla eklendi!")
        print(f"📊 Toplam işlenmemiş tweet sayısı: {count}")
        return True
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Veritabanına tweet gönderme işlemi başlıyor...")
    
    if not test_connection():
        print("❌ Bağlantı hatası! Lütfen .env dosyasını kontrol edin.")
        print(f"DB_HOST: {os.getenv('DB_HOST')}")
        print(f"DB_PORT: {os.getenv('DB_PORT')}")
        print(f"DB_NAME: {os.getenv('DB_NAME')}")
        print(f"DB_USER: {os.getenv('DB_USER')}")
        exit(1)
    
    check_database_status()
    
    print("\n📨 Tweet'ler ekleniyor...")
    success = insert_sample_tweets()
    
    if success:
        check_database_status()
        print("\n🎉 İşlem başarıyla tamamlandı!")
    else:
        print("\n💥 İşlem başarısız oldu!")
