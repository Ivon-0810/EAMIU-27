from flask import Blueprint, render_template, session, request, jsonify
from app.extensions import db
from app.models.models import Club, Joueur, Composition, CompositionJoueur

effectif_bp = Blueprint("effectif", __name__)


@effectif_bp.route("/effectif")
def voir_effectif():
    club = Club.query.get(session.get("club_id"))
    if not club:
        return render_template("choix_club.html", ligues=[])
    joueurs = sorted(club.effectif_actif(), key=lambda j: (j.poste_principal, -j.overall()))
    return render_template("effectif.html", club=club, joueurs=joueurs)


@effectif_bp.route("/composition", methods=["GET", "POST"])
def composition():
    club = Club.query.get(session.get("club_id"))
    joueurs = club.effectif_actif()

    if request.method == "POST":
        data = request.get_json()
        formation = data.get("formation", club.formation_favorite)
        titulaires_ids = data.get("titulaires", [])  # liste de {joueur_id, poste}

        club.formation_favorite = formation
        db.session.commit()
        return jsonify({"ok": True, "message": "Composition enregistrée"})

    return render_template("composition.html", club=club, joueurs=joueurs)


@effectif_bp.route("/joueur/<int:joueur_id>")
def fiche_joueur(joueur_id):
    joueur = Joueur.query.get_or_404(joueur_id)
    return render_template("fiche_joueur.html", joueur=joueur)
