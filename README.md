Origine : construit le 2026-10-03 à la demande de Léon, à partir de l'idée `../idee-site-carte-des-competences.md` et de l'export Notion Sedniner (`04 PROJET/bta/team-academy/notion-sedniner/`).
Date : 2026-10-03. Statut : en ligne depuis le 2026-10-09, sur https://1000xo.github.io/carte-competences/ (dépôt public https://github.com/1000xO/carte-competences), et sur Vercel depuis le 2026-10-20 : https://carte-competences.vercel.app
Usage : la carte des compétences de l'équipe (compétences, lectures, articles réflexifs, sessions de formation, et leurs liens), à ouvrir dans le navigateur.

# Site « Carte des compétences »

Pour le voir : double-clic sur `index.html`. Il faut une connexion internet, car la page charge sa police et la bibliothèque de dessin de la carte (d3) depuis internet.

## Ce qu'il contient

- **Carte** : la vue en graphe façon Obsidian, avec les mêmes réglages que la vue graphique Obsidian de Léon (taille des nœuds selon le nombre de liens, forces identiques). Les grands ronds sont les 14 compétences, les petits points les ressources, en trois nuances de bleu (foncé : LI, moyen : AR, clair : SF). Le mode « Compétences » ne garde que les 14 compétences, reliées entre elles selon le nombre de ressources qu'elles partagent. Un clic sur un point ouvre son détail, avec le lien vers la fiche Notion.
- **Compétences** : les 14 compétences en cartes, avec leur nombre de ressources et la part de théorie des niveaux déjà couverte. Un clic ouvre la page de la compétence : ses 5 niveaux (texte du référentiel, puis la théorie demandée, cochée si une ressource de l'équipe la couvre, « exigé » quand le référentiel demande explicitement une lecture), puis l'arbre (sous-compétences, LI, AR et SF). Lien direct : `index.html#C08`.
- **La molette** (en haut à gauche de la carte) : les réglages façon Obsidian (texte, taille des nœuds, liens, forces).
- **Ressources** : toutes les ressources dans un tableau, avec recherche et filtres (dont l'étape : validée, en cours, annoncée).
- **Ce qui arrive** : partout, une ressource pas encore validée est dessinée en anneau (contour sans remplissage). Une SF future compte comme « à venir ».
- **Trous** : les compétences les moins nourries en ressources validées, puis la théorie demandée par le référentiel que personne n'a encore couverte (idées de prochaines LI).
- **Donner un avis** : le bouton en bas à droite ouvre en pop up un formulaire Tally (idée, manque, souci, avis général). Les réponses arrivent dans Tally et par mail. Modifier le formulaire : https://tally.so/forms/pebxPy/edit
- **Comment ça marche** : le lien avec le modèle SECI de Nonaka et Takeuchi.

Chaque onglet s'ouvre aussi par un lien direct, par exemple `index.html#trous`.

## Les chiffres (export du 22 septembre 2026)

14 compétences, 147 LI, 93 AR et 17 SF reliées à au moins une compétence. 255 de ces 257 ressources ont leur lien Notion. Cinq ressources sont rattachées à 13 compétences à la fois : elles restent sur la carte mais ne comptent pas dans les liens entre compétences ni dans les trous.

## Mettre à jour

1. Dans ce dossier, lancer `python notion_direct.py` : il lit en direct les bases LI, AR, SF et Compétences du Notion Sedniner (quelques secondes, lecture seule) et les range dans `donnees-direct/`.
2. Puis `python contenus.py` : il lit le texte de chaque fiche LI et AR (lecture seule, seulement les fiches nouvelles ; `--tout` pour tout relire) et le range dans `donnees-direct/contenus.json`.
3. Puis lancer `python build.py`. Il relit ces données et réécrit `index.html`.

Si `donnees-direct/` n'existe pas, `build.py` reprend l'export complet (`04 PROJET/bta/team-academy/notion-sedniner/`).

Les changements successifs sont notés dans `historique-des-changements.md`.

`exigences.json` : la théorie demandée à chaque niveau, avec les mots-clés cherchés dans les titres. À corriger à la main si une coche est fausse. Après chaque `python build.py`, la liste de ce qui a été trouvé est dans `donnees-direct/verification-exigences.txt`.

`template.html` est le modèle de la page, `build.py` y injecte les données. On modifie le modèle, jamais `index.html` directement (il est écrasé à chaque mise à jour).

## Ce qui manque encore

- Les sous-compétences : à définir avec les responsables de compétence, puis à écrire dans `sous-competences.json` avant de relancer `python build.py`.
- Les noms (qui a fait quoi) : faits le 2026-10-23, responsable et suppléant de chaque compétence, auteurs de chaque ressource. Le Notion public cache les noms, ils viennent donc de `personnes.json` (identifiant Notion -> nom). Une nouvelle personne dans l'équipe : l'ajouter dans ce fichier, sinon son nom reste vide.

## Publier une mise à jour en ligne

Après `python notion_direct.py` puis `python build.py`, envoyer les changements sur GitHub (`git add -A`, `git commit`, `git push` dans ce dossier, ou le demander à Claude). Le site en ligne se met à jour en une à deux minutes.

Sur Vercel : dans ce dossier, lancer `npx vercel deploy --prod --yes` (compte Vercel de Léon, projet `carte-competences`). `.vercelignore` empêche l'envoi des données brutes (`donnees-direct/`).

`niveaux-vises.json` : combien de personnes visent chaque niveau ce semestre (totaux, sans noms). Les niveaux visés s'affichent ouverts sur la page de chaque compétence.

`criteres.json` : les critères des niveaux visés, une phrase du référentiel par critère, avec les mots-clés (français et anglais) cherchés dans le titre et le contenu des ressources. Un clic sur un critère montre les ressources qui en parlent. À corriger à la main si un lien est faux ou manque.

`synonymes.json` : les mots équivalents pour la recherche (« négociation » trouve aussi « negotiation »). La recherche de l'onglet Ressources regarde le titre, les auteurs, puis le contenu des fiches.

## Mesure d'audience (Microsoft Clarity)

Clarity est un outil gratuit de Microsoft qui montre comment les visiteurs utilisent le site : cartes de chaleur (où l'on clique), enregistrements anonymes des visites, pages les plus vues. L'emplacement est prêt dans `template.html` (`<!--CLARITY-->`), mais il reste vide tant que le fichier `clarity.txt` n'existe pas. Pour l'activer : créer un projet sur clarity.microsoft.com, copier son identifiant (une dizaine de lettres et chiffres, visible dans Paramètres > Installation) dans `clarity.txt`, puis `python build.py` et publier. Cet identifiant n'est pas secret (il apparaît dans la page), il peut donc aller dans le dépôt, ce qui garde Clarity actif après la mise à jour automatique du lundi.
