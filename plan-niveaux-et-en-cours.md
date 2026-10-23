Origine : demande de Léon du 2026-10-18 (« regarde aussi les LI en cours, tu peux rajouter cela au site » et « afficher les niveaux des compétences, mettre en évidence ce qui est explicitement demandé pour valider un niveau, et le cocher si une lecture est faite »), validée par « oui fais ça ».
Date : 2026-10-18.
Usage : le plan de l'ajout au site « carte des compétences », à suivre pendant la construction.

# Plan : ce qui est en cours, et les niveaux des compétences

## 1. Voir ce qui est en cours

Chaque ressource reçoit une étape tirée de son statut Notion : validée, en cours (lecture ou article commencé, feedback attendu), annoncée (annonce en préparation ou en validation). Une SF dont la date est passée compte comme suivie, une SF future comme à venir.

Sur la carte, une ressource pas encore validée est dessinée en anneau (contour de couleur, centre vide). Dans le tableau des ressources, le filtre « Validées seulement » devient un menu : toutes, validées, en cours, annoncées. Le panneau d'une compétence et son arbre séparent ce qui est validé de ce qui arrive.

## 2. Les niveaux dans l'arbre de chaque compétence

En haut de la page d'une compétence, les cinq niveaux du référentiel (texte officiel, `04 PROJET/bta/team-academy/Référentiel 14 compétences 2024 - 2025.md`). Sous chaque niveau, seulement ce qui relève de la théorie : les lectures exigées (marquées « exigé ») et les théories, modèles ou auteurs nommés. Les expériences pratiques restent dans le texte du niveau, pas dans la liste.

La liste est écrite à la main dans `exigences.json`, avec des mots-clés pour chaque élément.

## 3. La coche automatique

`build.py` cherche les mots-clés dans les titres des LI, AR et SF de l'équipe. Un élément est coché si une ressource validée le couvre, marqué « en cours » si seule une ressource pas encore validée le couvre, vide sinon. Par défaut, seules les ressources rattachées à la compétence comptent ; un auteur précis (Porter, Senge, effectuation) compte partout. Les exigences qui ne se voient pas dans un titre (workshop en anglais, AR en anglais) sont affichées « à prouver soi-même », sans coche.

Première vérification à la main : `build.py` imprime pour chaque élément les titres trouvés, à relire avant publication.

## Limites

Notion ne donne pas les noms des teampreneurs : la coche dit « l'équipe l'a couvert », pas qui. Le texte des niveaux est celui du référentiel officiel, publié tel quel sur le site public.

## Suite prévue, en attente des niveaux de chacun (ajouté le 2026-10-23)

Les niveaux sont masqués sur le site depuis le 2026-10-23, avec la mention « En cours » (page de chaque compétence, onglet Trous, et le compteur « Théorie des niveaux » des cartes). Ils sont prêts dans le code : passer `NIVEAUX_PRETS` à `true` dans `template.html` pour les réafficher.

Ce qui débloque la suite : le niveau actuel et le niveau visé ce semestre de chaque personne, par compétence, demandés par questionnaire Tally.

Idées de Léon pour après :

- Trois onglets de plus : « Niveaux », « Recommandations de lecture » et « En attente ».
- N'afficher que les niveaux utiles, d'après les niveaux visés. Si tout le monde a passé le niveau 2, on vise le 3, et le niveau 2 n'a plus besoin d'être mis en avant. Si quelques personnes visent un niveau au-dessus du reste de l'équipe, ce niveau s'affiche aussi.
- Les recommandations de lecture partent de la théorie demandée aux niveaux visés et pas encore couverte par l'équipe.

Décision du 2026-10-23 (Léon, puis avis de Claude) : pas d'onglets « Niveaux », « Recommandations » ni « En attente ». Tout va sur la page de chaque compétence, dans l'ordre niveaux, recommandations, ressources. « En attente » est déjà couvert par les anneaux et le filtre « Pas encore validées » de l'onglet Ressources. Piste à revoir une fois les niveaux reçus : une vue « mes recommandations » par personne, toutes compétences confondues.
