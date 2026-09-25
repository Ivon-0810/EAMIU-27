# Gestion Club — jeu de gestion de football (mode Président/Coach)

## Lancer le jeu (chez toi, en local)

```bash
cd gestion-club
python3 -m venv venv
source venv/bin/activate        # sous Windows : venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Puis ouvre http://127.0.0.1:5000 dans ton navigateur.

Au premier lancement, la base de données est créée automatiquement
(`instance/gestion_club.db`) et peuplée avec :
- Les 5 grands championnats européens (Premier League, LaLiga, Serie A,
  Bundesliga, Ligue 1) — clubs réels, saison 2026-2027
- La pyramide camerounaise : MTN Elite One (D1, 14 clubs) et
  MTN Elite Two (D2, où tu peux à terme créer ton propre club et
  monter en D1)
- 60 saisons, de 2026-2027 à 2085-2086
- Un effectif de ~23 joueurs générés pour chaque club (noms
  provisoires — à remplacer par un vrai import de données si tu
  veux des noms de joueurs réels, via un futur écran d'import CSV)

## Ce qui est déjà fonctionnel

- Choix du club de départ
- Visualisation de l'effectif complet (notes, forme, moral, contrat)
- Fiche détaillée par joueur
- Marché des transferts : rechercher un joueur, faire une offre
  (négociation simplifiée automatique), historique des transferts
- Jour de match : suivi minute par minute avec arrêt automatique à la
  mi-temps pour faire des changements, ou simulation instantanée du
  résultat

## Prochaines étapes possibles (à me dire ce que tu veux en premier)

1. **Écran de composition visuel** : glisser-déposer les titulaires
   sur un terrain (actuellement la formation se choisit en liste)
2. **Vraies données joueurs** : import CSV/API pour remplacer les
   noms générés par de vrais effectifs
3. **Calendrier de saison automatique** : génération des journées,
   classement en direct, fin de saison avec montées/descentes
   (y compris ta division D2 avec montée en D1)
3. **IA des autres clubs** : que les clubs non contrôlés fassent
   aussi des transferts et gèrent leur compo automatiquement
4. **Packaging desktop** avec PyInstaller (comme pour ITF), pour un
   exécutable autonome sans avoir à lancer Python manuellement
