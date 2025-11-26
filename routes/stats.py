from flask import Blueprint, jsonify
from db import get_conn, put_conn

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/stats", methods=["GET"])
def get_stats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS total_tweets,
            COUNT(CASE WHEN is_processed = TRUE THEN 1 END) AS processed_true,
            COUNT(CASE WHEN is_processed = FALSE THEN 1 END) AS processed_false
        FROM tweets_queue
    """)
    t = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM positive")
    positive_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM negative")
    negative_count = cur.fetchone()[0]

    put_conn(conn)

    return jsonify({
        "total_tweets": t[0],
        "processed_true": t[1],
        "processed_false": t[2],
        "positive_count": positive_count,
        "negative_count": negative_count
    }), 200
