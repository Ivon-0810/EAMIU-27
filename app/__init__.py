import os
from flask import Flask
from app.extensions import db


def create_app():
    app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "..", "instance", "gestion_club.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key-a-changer"

    db.init_app(app)

    from app.models import models  # noqa: F401  (enregistre les modèles)

    from app.routes.main import main_bp
    from app.routes.effectif import effectif_bp
    from app.routes.mercato import mercato_bp
    from app.routes.match_routes import match_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(effectif_bp)
    app.register_blueprint(mercato_bp)
    app.register_blueprint(match_bp)

    return app
