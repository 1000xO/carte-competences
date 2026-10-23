Origine : tenu par Claude au fil des sessions de travail sur le site.
Date : créé le 2026-10-03.
Usage : savoir ce qui a changé sur le site, pourquoi, et où on en est.

# Historique des changements du site « Carte des compétences »

## 2026-10-03 : style Apple, finitions

Statut : fait, vérifié par captures d'écran (ordinateur clair et sombre, mobile 390 px).

- Couleurs, typographie, panneaux en verre dépoli et cartes arrondies inspirés des sites Apple (fait en début de journée).
- Carte : la disposition est calculée avant l'affichage, puis cadrée entre les deux panneaux et affichée en fondu. Avant, le graphe bougeait au chargement et débordait sous les panneaux.
- Carte : les noms des compétences gardent la même taille à l'écran quel que soit le zoom. Quand la carte est très dézoomée (sur téléphone par exemple), seuls les numéros s'affichent, pour éviter que les noms se chevauchent.
- Ressources : les filtres tiennent sur une ligne, les menus déroulants ont un style sobre, les statuts sont affichés en pastilles (vertes quand la ressource est validée), les colonnes Type, Semestre et Notion ne se coupent plus.
- Mobile : la page ne dépasse plus de l'écran (onglets, tableau des ressources, menus déroulants).

## 2026-10-03 : écart de taille des points réduit

Statut : fait, vérifié par capture d'écran.

- À la demande de Léon, l'écart entre les ronds des compétences et les points des ressources est réduit : les compétences vont de 9 à 21 (au lieu de 10 à 32), les ressources passent de 4,5 à 6. Les ressources sont un peu plus espacées pour ne pas se toucher.

## 2026-10-03 : la carte reprend les réglages de la vue graphique Obsidian

Statut : fait, vérifié par captures d'écran (ordinateur et mobile). À la demande de Léon, d'après ses captures et le fichier `.obsidian/graph.json` du classeur.

- Réglages repris tels quels : force centrale 0,52, répulsion 10, force des liens 1, distance des liens 250, taille des nœuds 1, épaisseur des liens 1, fondu du texte 0, pas de flèches. Ils sont regroupés en haut du code (`OBSIDIAN`) pour pouvoir les changer facilement.
- Taille des nœuds calculée comme dans Obsidian : selon le nombre de liens, entre 8 et 30. Une ressource rattachée à une seule compétence est donc petite, une ressource transversale un peu plus grosse, une compétence plus grosse encore.
- Comme dans Obsidian, les nœuds gardent une taille lisible quand on dézoome, les liens restent fins à tout zoom, et les titres des ressources apparaissent quand on zoome.
- Le mode « Compétences » (14 ronds seulement) garde ses anciens réglages, puisqu'il n'a pas d'équivalent dans Obsidian.

## 2026-10-09

Demande de Léon : « il y a un bug avec certaines pages reliées à plein de compétences, je te laisse corriger ».

- Cinq LI étaient cochées sur 13 compétences dans Notion, sans doute un « tout cocher » par erreur : Rifkin, Branson, Kotter, Confessions d'un entrepreneur, Sempels.
- Notion garde l'ordre des coches. Le site ne garde donc que les compétences cochées avant la longue suite rangée dans l'ordre (02, 03, 04...), ou la première s'il n'y en a pas : Rifkin et Branson gardent la 02, Kotter la 04, Confessions la 14, Sempels les 02, 09 et 14.
- Une note le signale dans le détail de chacune de ces fiches.

Puis, retours de Léon sur le site (même jour) :

- Le panneau de gauche (Chercher, Afficher, Ressources, Statut) est retiré. À la place, une molette en haut à gauche, comme dans Obsidian, avec des curseurs : fondu du texte, taille des nœuds, épaisseur des liens, force centrale, force de répulsion, force des liens, distance des liens. Les réglages par défaut restent ceux d'Obsidian, et le navigateur retient ceux de chacun. Une petite légende reste en bas à gauche.
- La carte reste « vivante » : quand on tire un point ou qu'on bouge un curseur, elle se réorganise en douceur au lieu de se redessiner d'un coup.
- Bug corrigé : on ne pouvait plus sortir d'un point après avoir cliqué dessus. Maintenant, un clic dans le vide, un second clic sur le point, la touche Échap ou la croix du panneau ramènent à la vue d'ensemble.
- La force vers le centre est plus forte et les compétences s'écartent davantage entre elles, pour que le nuage forme un rond.
- Nouvelle page « arbre de la compétence » : un clic sur une compétence (carte de l'onglet Compétences, barre de l'onglet Trous, bouton dans le panneau de la carte) ouvre l'arbre, avec les sous-compétences (à définir) puis les LI, AR et SF. Lien direct possible, par exemple `index.html#C08`. Les sous-compétences se remplissent dans `sous-competences.json`, à définir avec les responsables de compétence.
- Les mentions des retours de projet sont retirées.
- Onglet Trous : la même règle de comptage partout (LI et AR validées, SF suivies), avec le détail LI, AR et SF pour chaque compétence et la date de l'export Notion. Le panneau de la carte compte de la même façon et liste à part les ressources en cours.

- Les données viennent maintenant de Notion en direct : `notion_direct.py` lit seulement les 4 bases utiles (LI, AR, SF, Compétences) en quelques secondes, au lieu de l'export complet de 3 300 pages. Résultat dans `donnees-direct/`, que `build.py` lit en priorité. Lecture du 2026-10-09 : 163 LI, 96 AR et 18 SF reliées à une compétence.
- Recherche de l'onglet Ressources plus tolérante : sans accents, et une ou deux fautes de frappe acceptées par mot. Demande de Léon, qui ne trouvait pas sa LI : elle est titrée « Enssentialism » dans Notion.
- Mise en ligne, avec l'accord de Léon (« public, en ligne ») : dépôt public https://github.com/1000xO/carte-competences et page web https://1000xo.github.io/carte-competences/ (GitHub Pages, gratuit). Les données brutes de `donnees-direct/` ne sont pas publiées.

## 2026-10-18 : données Notion remises à jour

Statut : fait en local, publication en ligne en attente de l'accord de Léon.

- Demande de Léon : « fetch les infos sur Notion pour qu'il soit à jour ». Relance de `notion_direct.py` puis `build.py`.
- Lecture du 2026-10-18 : 209 LI, 105 AR et 25 SF dans les bases, dont 168 LI, 100 AR et 18 SF reliées à une compétence (contre 163, 96 et 18 le 2026-10-09).

## 2026-10-18 : ce qui est en cours, et les niveaux des compétences

Statut : fait et vérifié dans le navigateur (carte, page d'une compétence, Trous), en local. Publication en attente de l'accord de Léon. Plan : `plan-niveaux-et-en-cours.md`.

- Demande de Léon : voir les LI en cours sur le site, afficher les niveaux des compétences, mettre en évidence la théorie explicitement demandée pour valider un niveau, et la cocher quand une lecture la couvre.
- Chaque ressource a une étape (validée, en cours, annoncée). Les ressources pas encore validées sont dessinées en anneau sur la carte et dans l'arbre. Le filtre « Validées seulement » est remplacé par un menu d'étapes. Les SF futures sont « à venir ».
- Page d'une compétence : les 5 niveaux du référentiel, avec sous chacun la théorie demandée (écrite à la main dans `exigences.json`), cochée automatiquement d'après les titres des LI, AR et SF de l'équipe. Les exigences invisibles dans un titre (workshop ou AR en anglais) sont marquées « à prouver soi-même ».
- Onglet Trous : nouvelle liste de la théorie demandée que personne ne couvre encore, compétence par compétence.
- Relecture à la main des coches : une dizaine de faux positifs corrigés (par exemple « Geoff Smart » pris pour les objectifs SMART, « Libérer la Suisse » pour l'entreprise libérée).

## 2026-10-20 : mise en ligne sur Vercel

Statut : fait et vérifié (page publique, données brutes non publiées).

- Demande de Léon : « push le site du knowledge manager sur Vercel ».
- Projet Vercel `carte-competences`, adresse https://carte-competences.vercel.app, avec la version locale du 18.10 (niveaux des compétences, ressources en cours).
- Ajout de `.vercelignore` pour ne pas envoyer `donnees-direct/`. La version GitHub Pages reste en ligne mais n'a pas encore la mise à jour du 18.10 (commit local pas encore poussé).

## 2026-10-20 : données Notion remises à jour

Statut : fait, en ligne sur Vercel et vérifié.

- Demande de Léon : « mets à jour avec le notion actuel le site ». Relance de `notion_direct.py` puis `build.py`, puis mise en ligne sur Vercel.
- Lecture du 2026-10-20 : 211 LI, 106 AR et 25 SF dans les bases, dont 170 LI, 100 AR et 18 SF reliées à une compétence (contre 168, 100 et 18 le 2026-10-18).

## 2026-10-20 : bouton « Donner un avis »

Statut : en ligne sur Vercel depuis le 2026-10-20 (vérifié). Le formulaire Tally reste à publier : tant qu'il ne l'est pas, la pop up s'ouvre mais reste vide.

- Demande de Léon : une pop up pour que les visiteurs donnent leur avis, sur le modèle des boutons « signaler un problème », mais pour les retours en général.
- Un bouton « 💬 Donner un avis » flotte en bas à droite de toutes les vues. Il ouvre en pop up le formulaire Tally « Ton avis sur la carte des compétences » (modifier : https://tally.so/forms/pebxPy/edit). Si Tally ne charge pas, le formulaire s'ouvre dans un nouvel onglet.
- Le formulaire : le genre de retour (idée, manque, quelque chose qui ne marche pas, avis général), le message, le prénom en facultatif. La vue d'où vient l'avis (carte, compétences, C08…) est notée toute seule dans un champ caché. Léon reçoit un mail à chaque réponse.
- Vérifié dans le navigateur : le bouton s'affiche et ouvre la pop up. Le contenu ne s'affichera qu'une fois le formulaire publié.

## 2026-10-20 : ouverture plus rapide de la pop up d'avis

Statut : fait en local, pas encore en ligne (à envoyer sur Vercel avec la prochaine mise à jour).

- Remarque de Léon : la pop up met longtemps à s'ouvrir. Cause principale : le formulaire Tally est encore en brouillon, la pop up attend un formulaire qui n'existe pas encore en public et tourne sans fin.
- Ajout d'une connexion préparée vers Tally dès le chargement de la page, pour gagner un peu de temps à l'ouverture une fois le formulaire publié.

## 2026-10-23 : « Qui demander », les noms derrière chaque ressource

Statut : fait en local et vérifié dans le navigateur (aucune erreur), pas encore en ligne. La publication attend l'accord de Léon, car le site est public et affiche maintenant les noms de l'équipe.

- Demande de Léon : savoir qui a fait quelle LI, pour trouver la personne compétente sur un sujet.
- Pourquoi les noms manquaient : le Notion public de Sedniner donne seulement des identifiants de personne et refuse de les traduire en noms (erreur 403). Les noms ont été relevés une fois depuis la session Notion de Léon dans Chrome, et rangés dans `personnes.json` (21 personnes, une inconnue). `notion_direct.py` s'en sert pour remplacer les « ‣ » par des noms.
- Page d'une compétence : nouvelle section « Qui demander », avec les personnes classées par nombre de LI et AR validées et de SF portées, puis ce qu'elles ont en cours. Le panneau de la carte en montre les 5 premières.
- Fiche d'une ressource : ses auteurs (ou les responsables, pour une SF), cliquables.
- Ressources : colonne « Par », filtre par personne, et la recherche trouve aussi les noms. Un clic sur un nom, n'importe où, ouvre cet onglet filtré sur la personne.
- Niveaux : l'info-bulle d'une ressource qui coche une théorie donne aussi ses auteurs.
- À savoir : quand une nouvelle personne apparaît dans Notion, son nom reste vide sur le site tant qu'on ne l'a pas ajoutée à `personnes.json`. `personnes.json` n'est pas envoyé sur GitHub.

## 2026-10-23 : liste « Qui demander » remplacée par le responsable de compétence

Statut : fait en local, pas encore en ligne.

- Retour de Léon : le but n'était pas d'afficher toute la liste des personnes. Vérification faite : dans 13 compétences sur 14, la personne en tête est à égalité avec la deuxième ou n'a qu'une ressource d'avance. Personne ne se démarque, un classement serait arbitraire.
- La liste classée est retirée (page de la compétence et panneau de la carte). À la place : le responsable de compétence et son suppléant, lus dans la base Compétences de Notion, cliquables.
- Gardés : les auteurs sur chaque ressource, la colonne « Par » et le filtre par personne de l'onglet Ressources.
- Piste pour plus tard : quand les responsables auront défini leurs tags (sous-catégories de l'arbre), regarder si une personne se démarque sur un tag. Sur une thématique plus fine, l'écart a plus de chances d'être net.

- Même jour, retour de Léon : le responsable et le suppléant sont affichés en texte simple, plus cliquables.

## 2026-10-23 : niveaux masqués, mention « En cours »

Statut : fait en local, pas encore en ligne.

- Demande de Léon : dire simplement que les niveaux sont en cours, en attendant le niveau actuel et le niveau visé de chacun.
- Page d'une compétence et onglet Trous : le détail des niveaux et la théorie non couverte sont remplacés par un encadré « En cours ». Le compteur « Théorie des niveaux » des cartes de compétence est masqué.
- Rien n'est supprimé : un interrupteur (`NIVEAUX_PRETS` dans `template.html`) les réaffiche. La suite prévue est dans `plan-niveaux-et-en-cours.md`.

- Même jour : section « Les recommandations » ajoutée sur la page de chaque compétence, entre les niveaux et les ressources, avec la mention « En cours ». Pas d'onglet à part (voir plan-niveaux-et-en-cours.md).
