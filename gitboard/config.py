from flask import Flask
from flask_redis import FlaskRedis

import logging
import os

redis = FlaskRedis()


def configure_logging(app):
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, app.config["LOG_LEVEL"].upper()))

    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    root.addHandler(handler)

    app.logger.addHandler(handler)


def create_app(**config):
    app = Flask(__name__)

    app.config.setdefault("LOG_LEVEL", "DEBUG")
    app.config.setdefault(
        "SECRET_KEY", os.environ.get("SECRET_KEY", "not very secretative")
    )
    app.config.setdefault(
        "REPOS",
        [
            "git@github.com:getsentry/sentry.git",
            "git@github.com:getsentry/getsentry.git",
        ],
    )
    app.config.setdefault("ALIASES", {})
    app.config.setdefault(
        "CACHE_DIR",
        os.path.join(os.getenv("USERPROFILE") or os.getenv("HOME"), ".gitboard"),
    )

    redis.init_app(app)

    configure_logging(app)

    return app
