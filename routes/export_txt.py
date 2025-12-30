from flask import Blueprint, send_file
from db import get_conn, put_conn
from io import BytesIO

export_bp = Blueprint("export", __name__, url_prefix="/api/export")

def _download_tweets_from_table(table_name: str, file_name: str):
    conn = get_conn()
    if not conn:
        return {'error': 'Database connection failed'}, 500

    try:
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT tweet_text 
            FROM {table_name} 
            ORDER BY created_at DESC
        """)

        tweets = cursor.fetchall()

        if not tweets:
            return {'error': f'No tweets found in {table_name}'}, 404

        tweet_texts = [row[0] for row in tweets]
        content = "\n".join(tweet_texts)

        txt_buffer = BytesIO()
        txt_buffer.write(content.encode('utf-8'))
        txt_buffer.seek(0)

        cursor.close()
        put_conn(conn)

        return send_file(
            txt_buffer,
            as_attachment=True,
            download_name=file_name,
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


@export_bp.route("/positive", methods=["GET"])
def download_positive_tweets():
    return _download_tweets_from_table("positive", "positive_tweets.txt")


@export_bp.route("/negative", methods=["GET"])
def download_negative_tweets():
    return _download_tweets_from_table("negative", "negative_tweets.txt")
