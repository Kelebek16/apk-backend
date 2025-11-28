from flask import Blueprint, request, jsonify
import traceback

from db import get_conn, put_conn

positive_labeled_bp = Blueprint("positive_labeled_bp", __name__)

@positive_labeled_bp.route("/labeled/positive", methods=["GET"])
def get_labeled_positive():
    conn = None
    try:
        batch_size = request.args.get("batch_size", 1000, type=int)
        last_id = request.args.get("last_id", 0, type=int)

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, data_id, tweet_text, created_at
            FROM positive
            WHERE id > %s
            ORDER BY id
            LIMIT %s;
            """,
            (last_id, batch_size),
        )

        rows = cur.fetchall()
        results = [
            {
                "id": row[0],
                "data_id": row[1],
                "tweet_text": row[2],
                "created_at": row[3].isoformat() if row[3] else None,
            }
            for row in rows
        ]

        new_last_id = results[-1]["id"] if results else last_id

        return (
            jsonify(
                {
                    "success": True,
                    "count": len(results),
                    "last_id": new_last_id,
                    "data": results,
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
