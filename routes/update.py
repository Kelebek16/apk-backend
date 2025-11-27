from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

update_tweet_bp = Blueprint("update_tweet", __name__)


@update_tweet_bp.route("/tweets/<int:tweet_id>", methods=["PUT"])
def update_tweet_text(tweet_id):
    data = request.get_json(silent=True) or {}
    new_text = data.get("tweet_text")

    if not new_text or not isinstance(new_text, str):
        return jsonify({"success": False, "message": "tweet_text zorunlu ve string olmalı"}), 400

    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            UPDATE tweets_queue
            SET tweet_text = %s
            WHERE id = %s
            RETURNING id, tweet_text, is_processed, label, created_at, processed_at
            """,
            (new_text, tweet_id),
        )
        updated_row = cur.fetchone()

        if not updated_row:
            conn.rollback()
            return jsonify({"success": False, "message": "Kayıt bulunamadı"}), 404

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Tweet metni güncellendi",
            "data": dict(updated_row),
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": "Hata oluştu", "error": str(e)}), 500

    finally:
        if conn:
            conn.close()
