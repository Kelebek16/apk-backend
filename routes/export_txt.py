from flask import Blueprint, send_file
from db import get_conn, put_conn
from io import BytesIO

download_bp = Blueprint("download", __name__, url_prefix="/api/download")

@download_bp.route("/positive", methods=["GET"])
def download_positive_tweets():
    conn = get_conn()
    if not conn:
        return {'error': 'Database connection failed'}, 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tweet_text 
            FROM positive 
            ORDER BY created_at DESC
        """)
        
        positive_tweets = cursor.fetchall()
        
        if not positive_tweets:
            return {'error': 'No positive tweets found'}, 404
        
        tweet_texts = [tweet[0] for tweet in positive_tweets]
        content = "\n".join(tweet_texts)
        
        txt_buffer = BytesIO()
        txt_buffer.write(content.encode('utf-8'))
        txt_buffer.seek(0)
        
        cursor.close()
        put_conn(conn)
        
        return send_file(
            txt_buffer,
            as_attachment=True,
            download_name='positive_tweets.txt',
            mimetype='text/plain'
        )
        
    except Exception as e:
        put_conn(conn)
        return {'error': str(e)}, 500
