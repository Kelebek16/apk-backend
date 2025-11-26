from flask import Blueprint, jsonify
from db import get_conn, put_conn

tweets_bp = Blueprint("tweets", __name__, url_prefix="/api/tweets")

@tweets_bp.route("/unprocessed", methods=["GET"])
def get_unprocessed_tweets():
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, tweet_text, created_at
            FROM tweets_queue
            WHERE is_processed = FALSE
            ORDER BY id;
            """
        )
        rows = cur.fetchall()
        results = [
            {
                "id": row[0],
                "tweet_text": row[1],
                "created_at": row[2].isoformat() if row[2] else None,
            }
            for row in rows
        ]
        return jsonify({"success": True, "count": len(results), "data": results}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn:
            put_conn(conn)

@tweets_bp.route("/label", methods=["POST"])
def label_tweet():
    data = request.get_json(silent=True) or {}
    tweet_id = data.get("id")
    label = data.get("label")

    if not tweet_id or label not in ("positive", "negative"):
        return jsonify({"success": False, "error": "id and label must be provided with value 'positive' or 'negative'"}), 400

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, tweet_text FROM tweets_queue WHERE id = %s AND is_processed = FALSE;",
            (tweet_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"success": False, "error": "tweet not found or already processed"}), 404

        data_id = row[0]
        tweet_text = row[1]

        table = "positive" if label == "positive" else "negative"

        cur.execute(
            f"INSERT INTO {table} (data_id, tweet_text) VALUES (%s, %s) RETURNING id;",
            (data_id, tweet_text),
        )
        target_id = cur.fetchone()[0]

        cur.execute(
            "UPDATE tweets_queue SET is_processed = TRUE, label = %s, processed_at = CURRENT_TIMESTAMP WHERE id = %s;",
            (label, data_id),
        )

        conn.commit()

        return jsonify(
            {
                "success": True,
                "tweet_id": data_id,
                "label": label,
                "target_id": target_id,
                "table": table,
            }
        ), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn:
            put_conn(conn)
