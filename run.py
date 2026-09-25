from app import create_app
from app.extensions import db
from app.data.seed_data import peupler_base
from app.data.generateur_joueurs import generer_effectifs

app = create_app()

with app.app_context():
    db.create_all()
    peupler_base()
    generer_effectifs()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
