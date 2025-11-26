from flask import Blueprint, send_file
from db import get_conn, put_conn
from io import BytesIO

export_bp = Blueprint("export", __name__, url_prefix="/api/export")

@export_bp.route("/positive", methods=["GET"])
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
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error occurred: {str(e)}")
        print(f"Traceback: {error_traceback}")
        
        if conn:
            put_conn(conn)
        return {
            'error': str(e),
            'traceback': error_traceback
        }, 500
