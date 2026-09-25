from flask import Blueprint, render_template, session, request, jsonify
from app.extensions import db
from app.models.models import (Club, Joueur, Match, Composition,
                                CompositionJoueur, EvenementMatch)
from app.services import moteur_match

match_bp = Blueprint("match", __name__)


def _stats_equipe(club, composition):
    titulaires_ids = [cj.joueur_id for cj in composition.titulaires if cj.est_titulaire]
    joueurs = Joueur.query.filter(Joueur.id.in_(titulaires_ids)).all() if titulaires_ids else []
    return {
        "attaque": moteur_match.force_offensive(joueurs),
        "defense": moteur_match.force_defensive(joueurs),
    }


@match_bp.route("/match/<int:match_id>")
def jour_de_match(match_id):
    match = Match.query.get_or_404(match_id)
    return render_template("match.html", match=match)


@match_bp.route("/match/<int:match_id>/avancer", methods=["POST"])
def avancer_match(match_id):
    """Avance le match de plusieurs minutes (appelé par l'interface
    'direct'). S'arrête automatiquement à la 45e (mi-temps) pour
    permettre les changements, puis à la 90e."""
    match = Match.query.get_or_404(match_id)
    comp_dom = Composition.query.filter_by(match_id=match.id,
                                            club_id=match.club_domicile_id).first()
    comp_ext = Composition.query.filter_by(match_id=match.id,
                                            club_id=match.club_exterieur_id).first()
    stats_dom = _stats_equipe(None, comp_dom)
    stats_ext = _stats_equipe(None, comp_ext)

    minutes_cibles = [45, 90]
    prochaine_pause = next((m for m in minutes_cibles if m > match.minute_courante), 90)

    nouveaux_evenements = []
    while match.minute_courante < prochaine_pause:
        match.minute_courante += 1
        evts = moteur_match.simuler_minute(match.minute_courante, stats_dom, stats_ext)
        for e in evts:
            club_id = match.club_domicile_id if e["equipe"] == "domicile" else match.club_exterieur_id
            if e["type"] == "but":
                if e["equipe"] == "domicile":
                    match.score_domicile = (match.score_domicile or 0) + 1
                else:
                    match.score_exterieur = (match.score_exterieur or 0) + 1
            ev = EvenementMatch(match_id=match.id, minute=e["minute"],
                                 type_evenement=e["type"], club_id=club_id)
            db.session.add(ev)
            nouveaux_evenements.append({"minute": e["minute"], "type": e["type"],
                                         "equipe": e["equipe"]})

    if match.minute_courante >= 90:
        match.statut = "termine"
    elif match.minute_courante >= 45:
        match.statut = "mi_temps"
    else:
        match.statut = "en_cours"

    db.session.commit()
    return jsonify({
        "minute": match.minute_courante,
        "score_domicile": match.score_domicile,
        "score_exterieur": match.score_exterieur,
        "statut": match.statut,
        "evenements": nouveaux_evenements,
    })


@match_bp.route("/match/<int:match_id>/changement", methods=["POST"])
def faire_changement(match_id):
    """Remplacement pendant le match ou à la mi-temps. Ne déplace pas
    de joueur sur un terrain : met simplement à jour la composition
    (sortant -> statut, entrant -> titulaire)."""
    match = Match.query.get_or_404(match_id)
    data = request.get_json()
    composition_id = data["composition_id"]
    joueur_sortant_id = data["joueur_sortant_id"]
    joueur_entrant_id = data["joueur_entrant_id"]

    cj_sortant = CompositionJoueur.query.filter_by(
        composition_id=composition_id, joueur_id=joueur_sortant_id).first()
    cj_entrant = CompositionJoueur.query.filter_by(
        composition_id=composition_id, joueur_id=joueur_entrant_id).first()

    if not cj_sortant or not cj_entrant:
        return jsonify({"ok": False, "message": "Joueur introuvable dans la composition"}), 400

    cj_sortant.est_titulaire = False
    cj_sortant.sorti_minute = match.minute_courante
    cj_entrant.est_titulaire = True
    cj_entrant.poste_occupe = cj_sortant.poste_occupe

    ev = EvenementMatch(match_id=match.id, minute=match.minute_courante,
                         type_evenement="changement", joueur_id=joueur_sortant_id,
                         joueur_entrant_id=joueur_entrant_id)
    db.session.add(ev)
    db.session.commit()
    return jsonify({"ok": True})


@match_bp.route("/match/<int:match_id>/simuler", methods=["POST"])
def simuler_instantanement(match_id):
    """Le joueur choisit de ne pas suivre le match minute par minute :
    on calcule directement le résultat final."""
    match = Match.query.get_or_404(match_id)
    comp_dom = Composition.query.filter_by(match_id=match.id,
                                            club_id=match.club_domicile_id).first()
    comp_ext = Composition.query.filter_by(match_id=match.id,
                                            club_id=match.club_exterieur_id).first()
    stats_dom = _stats_equipe(None, comp_dom)
    stats_ext = _stats_equipe(None, comp_ext)

    score_dom, score_ext, evenements = moteur_match.simuler_match_complet(stats_dom, stats_ext)
    match.score_domicile = score_dom
    match.score_exterieur = score_ext
    match.minute_courante = 90
    match.statut = "simule"
    db.session.commit()

    return jsonify({"score_domicile": score_dom, "score_exterieur": score_ext,
                     "evenements": evenements})
