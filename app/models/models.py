"""
Modèles de données du jeu de gestion de club.
Couvre : ligues/divisions, clubs, joueurs, saisons, calendrier,
transferts, matchs (avec remplacements), et compositions.
"""
from datetime import datetime
from app.extensions import db


# ---------------------------------------------------------------------------
# LIGUES & DIVISIONS
# ---------------------------------------------------------------------------

class Confederation(db.Model):
    __tablename__ = "confederations"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)  # UEFA, CAF...
    pays = db.relationship("Pays", backref="confederation", lazy=True)


class Pays(db.Model):
    __tablename__ = "pays"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    code_iso = db.Column(db.String(3))
    confederation_id = db.Column(db.Integer, db.ForeignKey("confederations.id"))
    ligues = db.relationship("Ligue", backref="pays", lazy=True)


class Ligue(db.Model):
    """Une ligue = une pyramide nationale (ex: 'France'). Contient
    plusieurs Division (D1, D2...)."""
    __tablename__ = "ligues"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)  # ex: "Championnat de France"
    pays_id = db.Column(db.Integer, db.ForeignKey("pays.id"))
    divisions = db.relationship("Division", backref="ligue", lazy=True,
                                 order_by="Division.niveau")


class Division(db.Model):
    """Un niveau de la pyramide (D1, D2...) avec ses règles de
    montée/descente."""
    __tablename__ = "divisions"
    id = db.Column(db.Integer, primary_key=True)
    ligue_id = db.Column(db.Integer, db.ForeignKey("ligues.id"), nullable=False)
    nom = db.Column(db.String(120), nullable=False)  # ex: "Ligue 1", "MTN Elite One"
    niveau = db.Column(db.Integer, nullable=False)  # 1 = D1, 2 = D2...
    nb_clubs = db.Column(db.Integer, default=18)
    nb_montants = db.Column(db.Integer, default=0)   # places de montée vers niveau-1
    nb_relegues = db.Column(db.Integer, default=0)   # places de descente vers niveau+1
    autorise_creation_club = db.Column(db.Boolean, default=False)
    clubs = db.relationship("Club", backref="division", lazy=True)


# ---------------------------------------------------------------------------
# CLUBS
# ---------------------------------------------------------------------------

class Club(db.Model):
    __tablename__ = "clubs"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    ville = db.Column(db.String(120))
    division_id = db.Column(db.Integer, db.ForeignKey("divisions.id"), nullable=False)
    est_club_joueur = db.Column(db.Boolean, default=False)  # club créé/contrôlé par l'utilisateur
    budget = db.Column(db.Float, default=1_000_000.0)
    reputation = db.Column(db.Integer, default=50)  # 1-100, influe sur négociations
    couleur_1 = db.Column(db.String(7), default="#1a1a2e")
    couleur_2 = db.Column(db.String(7), default="#ffffff")
    formation_favorite = db.Column(db.String(10), default="4-4-2")

    joueurs = db.relationship("Joueur", backref="club", lazy=True,
                               foreign_keys="Joueur.club_id")

    def effectif_actif(self):
        return [j for j in self.joueurs if j.statut == "actif"]


# ---------------------------------------------------------------------------
# JOUEURS
# ---------------------------------------------------------------------------

POSTES = [
    "GB",                                   # Gardien
    "DC", "DD", "DG",                       # Défenseurs
    "MDC", "MC", "MD", "MG", "MOC",         # Milieux
    "AD", "AG", "BU",                       # Attaquants
]


class Joueur(db.Model):
    __tablename__ = "joueurs"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    date_naissance = db.Column(db.Date)
    nationalite = db.Column(db.String(80))
    poste_principal = db.Column(db.String(5))
    postes_secondaires = db.Column(db.String(40))  # ex: "MC,MD"

    # Attributs (0-99, comme un vrai moteur de simulation)
    attaque = db.Column(db.Integer, default=50)
    defense = db.Column(db.Integer, default=50)
    passe = db.Column(db.Integer, default=50)
    physique = db.Column(db.Integer, default=50)
    vitesse = db.Column(db.Integer, default=50)
    technique = db.Column(db.Integer, default=50)
    mental = db.Column(db.Integer, default=50)
    potentiel = db.Column(db.Integer, default=50)  # plafond de progression

    forme = db.Column(db.Integer, default=70)      # 0-100, varie selon les matchs
    moral = db.Column(db.Integer, default=70)       # 0-100
    fatigue = db.Column(db.Integer, default=0)      # 0-100
    blessure_jours_restants = db.Column(db.Integer, default=0)

    valeur_marchande = db.Column(db.Float, default=100_000.0)
    salaire_mensuel = db.Column(db.Float, default=1000.0)
    fin_contrat = db.Column(db.Date)

    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    statut = db.Column(db.String(20), default="actif")  # actif / prêté / libre

    def age(self, date_reference=None):
        ref = date_reference or datetime.utcnow().date()
        if not self.date_naissance:
            return None
        return ref.year - self.date_naissance.year - (
            (ref.month, ref.day) < (self.date_naissance.month, self.date_naissance.day)
        )

    def overall(self):
        """Note globale simplifiée pondérée par poste."""
        base = (self.attaque + self.defense + self.passe +
                self.physique + self.vitesse + self.technique + self.mental) / 7
        return round(base)


# ---------------------------------------------------------------------------
# SAISONS & CALENDRIER
# ---------------------------------------------------------------------------

class Saison(db.Model):
    __tablename__ = "saisons"
    id = db.Column(db.Integer, primary_key=True)
    annee_debut = db.Column(db.Integer, nullable=False)  # 2026 -> saison 2026-2027
    annee_fin = db.Column(db.Integer, nullable=False)
    est_courante = db.Column(db.Boolean, default=False)


class Match(db.Model):
    __tablename__ = "matchs"
    id = db.Column(db.Integer, primary_key=True)
    saison_id = db.Column(db.Integer, db.ForeignKey("saisons.id"))
    division_id = db.Column(db.Integer, db.ForeignKey("divisions.id"))
    journee = db.Column(db.Integer)
    date_match = db.Column(db.DateTime)

    club_domicile_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    club_exterieur_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))

    score_domicile = db.Column(db.Integer)
    score_exterieur = db.Column(db.Integer)
    statut = db.Column(db.String(20), default="a_jouer")
    # a_jouer / en_cours (mi-temps incluse) / termine / simule

    minute_courante = db.Column(db.Integer, default=0)

    evenements = db.relationship("EvenementMatch", backref="match", lazy=True,
                                  order_by="EvenementMatch.minute")


class EvenementMatch(db.Model):
    """Un évènement du direct : but, carton, changement, mi-temps..."""
    __tablename__ = "evenements_match"
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matchs.id"), nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    type_evenement = db.Column(db.String(30))  # but, carton_jaune, carton_rouge,
    # changement, blessure, mi_temps, fin_match
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    joueur_id = db.Column(db.Integer, db.ForeignKey("joueurs.id"))
    joueur_entrant_id = db.Column(db.Integer, db.ForeignKey("joueurs.id"))
    description = db.Column(db.String(255))


class Composition(db.Model):
    """La feuille de match d'un club pour un match donné : onze de
    départ, remplaçants, et tactique."""
    __tablename__ = "compositions"
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matchs.id"), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    formation = db.Column(db.String(10), default="4-4-2")
    consignes = db.Column(db.String(30), default="equilibre")
    # offensif / equilibre / defensif

    titulaires = db.relationship("CompositionJoueur", backref="composition",
                                  lazy=True)


class CompositionJoueur(db.Model):
    __tablename__ = "composition_joueurs"
    id = db.Column(db.Integer, primary_key=True)
    composition_id = db.Column(db.Integer, db.ForeignKey("compositions.id"))
    joueur_id = db.Column(db.Integer, db.ForeignKey("joueurs.id"))
    poste_occupe = db.Column(db.String(5))
    est_titulaire = db.Column(db.Boolean, default=True)
    sorti_minute = db.Column(db.Integer, nullable=True)


# ---------------------------------------------------------------------------
# TRANSFERTS
# ---------------------------------------------------------------------------

class Transfert(db.Model):
    __tablename__ = "transferts"
    id = db.Column(db.Integer, primary_key=True)
    joueur_id = db.Column(db.Integer, db.ForeignKey("joueurs.id"), nullable=False)
    club_vendeur_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    club_acheteur_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    montant = db.Column(db.Float, default=0.0)
    type_operation = db.Column(db.String(20), default="transfert")
    # transfert / pret / fin_contrat / clause_rachat
    date_operation = db.Column(db.DateTime, default=datetime.utcnow)
    saison_id = db.Column(db.Integer, db.ForeignKey("saisons.id"))
    statut = db.Column(db.String(20), default="en_negociation")
    # en_negociation / acceptee / refusee / finalisee
