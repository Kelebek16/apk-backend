from flask import Blueprint, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

delete_tweet_bp = Blueprint("delete_tweet", __name__)

@delete_tweet_bp.route("/tweets/<int:tweet_id>", methods=["DELETE"])
def delete_tweet(tweet_id):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT id, tweet_text FROM tweets_queue WHERE id = %s",
            (tweet_id,)
        )
        row = cur.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Tweet bulunamadı"}), 404

        cur.execute("DELETE FROM tweets_queue WHERE id = %s", (tweet_id,))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Tweet başarıyla silindi",
            "deleted_id": row["id"],
            "deleted_text": row["tweet_text"],
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": "Hata oluştu", "error": str(e)}), 500

    finally:
        if conn:
            conn.close()
