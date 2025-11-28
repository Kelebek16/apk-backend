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
            """
            SELECT id, tweet_text, is_processed, label
            FROM tweets_queue
            WHERE id = %s
            """,
            (tweet_id,)
        )
        row = cur.fetchone()

        deleted_source = None
        queue_id_to_delete = None

        if row:
            queue_id_to_delete = row["id"]
            deleted_text = row["tweet_text"]
            deleted_source = "queue"
        else:
            cur.execute(
                """
                SELECT id, data_id, tweet_text
                FROM positive
                WHERE id = %s
                """,
                (tweet_id,)
            )
            prow = cur.fetchone()

            if prow:
                queue_id_to_delete = prow["data_id"]
                deleted_text = prow["tweet_text"]
                deleted_source = "positive"
            else:
                cur.execute(
                    """
                    SELECT id, data_id, tweet_text
                    FROM negative
                    WHERE id = %s
                    """,
                    (tweet_id,)
                )
                nrow = cur.fetchone()
                if nrow:
                    queue_id_to_delete = nrow["data_id"]
                    deleted_text = nrow["tweet_text"]
                    deleted_source = "negative"

        if not queue_id_to_delete:
            return jsonify({"success": False, "message": "Tweet bulunamadı"}), 404

        cur.execute("DELETE FROM tweets_queue WHERE id = %s", (queue_id_to_delete,))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Tweet başarıyla silindi",
            "deleted_queue_id": queue_id_to_delete,
            "deleted_from": deleted_source,
            "deleted_text": deleted_text,
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": "Hata oluştu", "error": str(e)}), 500

    finally:
        if conn:
            conn.close()
