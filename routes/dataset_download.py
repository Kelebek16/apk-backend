from flask import Blueprint, send_file, jsonify
import io
import zipfile
import traceback

from db import get_conn, put_conn

dataset_download_bp = Blueprint("dataset_download_bp", __name__)


@dataset_download_bp.route("/download_txt", methods=["GET"])
def download_txt():
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT tweet_text
            FROM positive
            ORDER BY id
        """)
        positives = [
            row[0].strip()
            for row in cur.fetchall()
            if row[0]
        ]

        cur.execute("""
            SELECT tweet_text
            FROM negative
            ORDER BY id
        """)
        negatives = [
            row[0].strip()
            for row in cur.fetchall()
            if row[0]
        ]

        cur.execute("""
            SELECT tweet_text
            FROM tweets_queue
            ORDER BY id
        """)
        queue_data = [
            row[0].strip()
            for row in cur.fetchall()
            if row[0]
        ]

        positive_txt = "\n".join(positives)
        negative_txt = "\n".join(negatives)
        queue_txt = "\n".join(queue_data)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("positive.txt", positive_txt)
            zipf.writestr("negative.txt", negative_txt)
            zipf.writestr("tweets_queue.txt", queue_txt)

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="tweet_dataset.zip"
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
