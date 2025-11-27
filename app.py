from flask import Flask
from config import Config
from routes.tweets import tweets_bp
from routes.export_txt import export_bp
from routes.stats import stats_bp
from routes.delete_tweet import delete_tweet_bp
from routes.update_tweet import update_tweet_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(update_tweet_bp)
    app.register_blueprint(delete_tweet_bp)
    app.register_blueprint(tweets_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(stats_bp)



    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="31.97.214.123", port=5000, debug=True)
