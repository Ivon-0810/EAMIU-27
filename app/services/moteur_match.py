"""
Moteur de match statistique.

Principe : à chaque minute, on calcule une probabilité d'évènement
(but, carton...) pour chaque équipe en fonction de la force globale
de la composition alignée (attaque vs défense adverse, forme, moral,
fatigue). Le joueur peut suivre le match minute par minute et faire
des changements, ou demander une simulation instantanée qui déroule
tout le calcul d'un coup sans passer par l'interface évènement par
évènement.
"""
import random


def force_offensive(joueurs_titulaires):
    if not joueurs_titulaires:
        return 40
    valeurs = [
        (j.attaque * 0.4 + j.technique * 0.3 + j.vitesse * 0.3)
        * (j.forme / 100) * (1 - j.fatigue / 200)
        for j in joueurs_titulaires
    ]
    return sum(valeurs) / len(valeurs)


def force_defensive(joueurs_titulaires):
    if not joueurs_titulaires:
        return 40
    valeurs = [
        (j.defense * 0.5 + j.physique * 0.3 + j.mental * 0.2)
        * (j.forme / 100) * (1 - j.fatigue / 200)
        for j in joueurs_titulaires
    ]
    return sum(valeurs) / len(valeurs)


def probabilite_but_par_minute(force_attaque, force_defense_adverse):
    """Renvoie une probabilité (0-1) qu'un but soit marqué sur une
    minute donnée. Calibré pour ~2.6 buts/match en moyenne (proche
    des standards observés dans les grands championnats)."""
    ratio = force_attaque / max(force_defense_adverse, 1)
    base = 0.013 * ratio  # ~1.2 but/équipe/match en moyenne si ratio=1
    return max(0.0, min(base, 0.08))


def simuler_minute(minute, equipe_dom_stats, equipe_ext_stats):
    """Renvoie une liste d'évènements (dict) survenus à cette minute."""
    evenements = []

    p_dom = probabilite_but_par_minute(equipe_dom_stats["attaque"], equipe_ext_stats["defense"])
    p_ext = probabilite_but_par_minute(equipe_ext_stats["attaque"], equipe_dom_stats["defense"])

    if random.random() < p_dom:
        evenements.append({"minute": minute, "type": "but", "equipe": "domicile"})
    if random.random() < p_ext:
        evenements.append({"minute": minute, "type": "but", "equipe": "exterieur"})

    # Cartons (rares)
    if random.random() < 0.004:
        evenements.append({"minute": minute, "type": "carton_jaune",
                            "equipe": random.choice(["domicile", "exterieur"])})

    return evenements


def simuler_match_complet(equipe_dom_stats, equipe_ext_stats):
    """Simulation instantanée : renvoie (score_dom, score_ext, evenements)."""
    score_dom, score_ext = 0, 0
    tous_evenements = []
    for minute in range(1, 91):
        evts = simuler_minute(minute, equipe_dom_stats, equipe_ext_stats)
        for e in evts:
            if e["type"] == "but":
                if e["equipe"] == "domicile":
                    score_dom += 1
                else:
                    score_ext += 1
        tous_evenements.extend(evts)
    return score_dom, score_ext, tous_evenements
