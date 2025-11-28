from flask import Blueprint, request, jsonify
import traceback
from db import get_conn, put_conn

add_positive_bp = Blueprint("add_positive_bp", __name__)


@add_positive_bp.route("/add_positive", methods=["POST"])
def add_positive():
    data = request.get_json(silent=True) or {}
    tweet_text = data.get("tweet_text")
    data_id = data.get("data_id")

    if not tweet_text:
        return jsonify({"success": False, "error": "tweet_text gerekli"}), 400

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO positive (data_id, tweet_text)
            VALUES (%s, %s)
            RETURNING id;
            """,
            (data_id, tweet_text),
        )
        new_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({
            "success": True,
            "inserted_id": new_id,
            "table": "positive",
            "tweet_text": tweet_text,
            "data_id": data_id
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()

        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }), 500

    finally:
        if conn:
            put_conn(conn)
