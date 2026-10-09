Origine : construit le 2026-10-03 à la demande de Léon, à partir de l'idée `../idee-site-carte-des-competences.md` et de l'export Notion Sedniner (`04 PROJET/bta/team-academy/notion-sedniner/`).
Date : 2026-10-03. Statut : en ligne depuis le 2026-10-09, sur https://1000xo.github.io/carte-competences/ (dépôt public https://github.com/1000xO/carte-competences).
Usage : la carte des compétences de l'équipe (compétences, lectures, articles réflexifs, sessions de formation, et leurs liens), à ouvrir dans le navigateur.

# Site « Carte des compétences »

Pour le voir : double-clic sur `index.html`. Il faut une connexion internet, car la page charge sa police et la bibliothèque de dessin de la carte (d3) depuis internet.

## Ce qu'il contient

- **Carte** : la vue en graphe façon Obsidian, avec les mêmes réglages que la vue graphique Obsidian de Léon (taille des nœuds selon le nombre de liens, forces identiques). Les grands ronds sont les 14 compétences, les petits points les ressources (bleu : LI, orange : AR, vert : SF). Le mode « Compétences » ne garde que les 14 compétences, reliées entre elles selon le nombre de ressources qu'elles partagent. Un clic sur un point ouvre son détail, avec le lien vers la fiche Notion.
- **Compétences** : les 14 compétences en cartes, avec leur nombre de ressources. Un clic ouvre l'arbre de la compétence (sous-compétences, puis LI, AR et SF). Lien direct : `index.html#C08`.
- **La molette** (en haut à gauche de la carte) : les réglages façon Obsidian (texte, taille des nœuds, liens, forces).
- **Ressources** : toutes les ressources dans un tableau, avec recherche et filtres.
- **Trous** : les compétences les moins nourries en ressources validées.
- **Comment ça marche** : le lien avec le modèle SECI de Nonaka et Takeuchi.

Chaque onglet s'ouvre aussi par un lien direct, par exemple `index.html#trous`.

## Les chiffres (export du 22 septembre 2026)

14 compétences, 147 LI, 93 AR et 17 SF reliées à au moins une compétence. 255 de ces 257 ressources ont leur lien Notion. Cinq ressources sont rattachées à 13 compétences à la fois : elles restent sur la carte mais ne comptent pas dans les liens entre compétences ni dans les trous.

## Mettre à jour

1. Dans ce dossier, lancer `python notion_direct.py` : il lit en direct les bases LI, AR, SF et Compétences du Notion Sedniner (quelques secondes, lecture seule) et les range dans `donnees-direct/`.
2. Puis lancer `python build.py`. Il relit ces données et réécrit `index.html`.

Si `donnees-direct/` n'existe pas, `build.py` reprend l'export complet (`04 PROJET/bta/team-academy/notion-sedniner/`).

Les changements successifs sont notés dans `historique-des-changements.md`.

`template.html` est le modèle de la page, `build.py` y injecte les données. On modifie le modèle, jamais `index.html` directement (il est écrasé à chaque mise à jour).

## Ce qui manque encore

- Les sous-compétences : à définir avec les responsables de compétence, puis à écrire dans `sous-competences.json` avant de relancer `python build.py`.
- Les personnes ressources (les noms ne remontent pas du Notion public, et il faut l'accord des personnes).

## Publier une mise à jour en ligne

Après `python notion_direct.py` puis `python build.py`, envoyer les changements sur GitHub (`git add -A`, `git commit`, `git push` dans ce dossier, ou le demander à Claude). Le site en ligne se met à jour en une à deux minutes.
