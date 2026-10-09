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
