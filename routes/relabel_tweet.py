from flask import Blueprint, request, jsonify
import traceback

from db import get_conn, put_conn

relabel_tweet_bp = Blueprint("relabel_tweet_bp", __name__, url_prefix="/tweets")


@relabel_tweet_bp.route("/relabel", methods=["POST"])
def relabel_tweet():
    data = request.get_json(silent=True) or {}
    tweet_id = data.get("id")
    new_label = data.get("label")

    if not tweet_id or new_label not in ("positive", "negative"):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "id and label ('positive' or 'negative') must be provided",
                }
            ),
            400,
        )

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, tweet_text, label FROM tweets_queue WHERE id = %s AND is_processed = TRUE;",
            (tweet_id,),
        )
        row = cur.fetchone()
        if not row:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "tweet not found or not processed yet",
                    }
                ),
                404,
            )

        data_id = row[0]
        tweet_text = row[1]
        old_label = row[2]

        if old_label not in ("positive", "negative"):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"current label is '{old_label}', cannot relabel",
                    }
                ),
                400,
            )

        if old_label == new_label:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "label is already set to requested value",
                        "tweet_id": data_id,
                        "label": old_label,
                    }
                ),
                200,
            )

        if old_label == "positive" and new_label == "negative":
            cur.execute("DELETE FROM positive WHERE data_id = %s;", (data_id,))
            cur.execute(
                "INSERT INTO negative (data_id, tweet_text) VALUES (%s, %s) RETURNING id;",
                (data_id, tweet_text),
            )
            target_table = "negative"
            target_id = cur.fetchone()[0]
        elif old_label == "negative" and new_label == "positive":
            cur.execute("DELETE FROM negative WHERE data_id = %s;", (data_id,))
            cur.execute(
                "INSERT INTO positive (data_id, tweet_text) VALUES (%s, %s) RETURNING id;",
                (data_id, tweet_text),
            )
            target_table = "positive"
            target_id = cur.fetchone()[0]
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"unsupported relabel from '{old_label}' to '{new_label}'",
                    }
                ),
                400,
            )

        cur.execute(
            "UPDATE tweets_queue SET label = %s, processed_at = CURRENT_TIMESTAMP WHERE id = %s;",
            (new_label, data_id),
        )

        conn.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "tweet_id": data_id,
                    "old_label": old_label,
                    "new_label": new_label,
                    "target_table": target_table,
                    "target_id": target_id,
                }
            ),
            200,
        )
    except Exception as e:
        if conn:
            conn.rollback()
        traceback.print_exc()
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )
    finally:
        if conn:
            put_conn(conn)
