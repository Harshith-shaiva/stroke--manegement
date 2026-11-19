# app/__init__.py
# Flask application factory.

import logging
from flask import Flask


def create_app(config_object: str = "config.ProductionConfig") -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_object: dotted path to a config class, e.g.
                       "config.DevelopmentConfig" or "config.ProductionConfig".
    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # ── Logging ──────────────────────────────────────────────────────────────
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    # ── Blueprints ───────────────────────────────────────────────────────────
    from .routes import bp, ui_bp
    app.register_blueprint(ui_bp)
    app.register_blueprint(bp)

    return app
