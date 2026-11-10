"""Génère le site « carte des compétences » à partir de l'export Notion Sedniner.

Lit les fichiers Markdown de 04 PROJET/bta/team-academy/notion-sedniner/
(LI, AR, SF, compétences), en tire les ressources et leurs compétences,
puis remplit template.html pour produire index.html (un seul fichier, à
ouvrir dans le navigateur).

Lancer : python build.py
"""

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ICI = Path(__file__).resolve().parent
EXPORT = ICI.parents[2] / "bta" / "team-academy" / "notion-sedniner"
# Si la lecture directe des 4 bases a été faite (notion_direct.py), on part de là : c'est plus récent
if (ICI / "donnees-direct" / "competences.md").exists():
    EXPORT = ICI / "donnees-direct"
NOTION = "https://chief-zinnia-fe9.notion.site/"
# Copie du référentiel dans le site (la mise à jour automatique sur GitHub n'a pas le reste du classeur)
REFERENTIEL = ICI / "referentiel.md"
if not REFERENTIEL.exists():
    REFERENTIEL = ICI.parents[2] / "bta" / "team-academy" / "Référentiel 14 compétences 2024 - 2025.md"

# Experts des SF : noms tels qu'écrits dans Notion -> nom(s) corrigé(s)
EXPERTS_CORRECTIONS = {
    "Maria Pia": ["Maria-Pia Vullyamoz"],
    "Marie -Charlotte Bagnoud": ["Marie-Charlotte Bagnoud"],
    "Beverly Todeschini Monica Zumstein": ["Beverly Todeschini", "Monica Zumstein"],
}


def experts(valeur):
    noms = []
    for n in valeur.split(","):
        n = " ".join(n.split())
        if n:
            noms += EXPERTS_CORRECTIONS.get(n, [n])
    return noms

SOURCES = [
    ("LI", "lectures-individuelles-li.md"),
    ("AR", "articles-reflexifs-ar.md"),
    ("SF", "sessions-de-formation-sf.md"),
]

# Statuts considérés comme « validés » (ressource terminée et acceptée)
VALIDES = {"LI Validée", "AR Validé"}


def etape(type_, statut, quand):
    """Où en est la ressource : validee, encours (lecture ou article commencé, feedback attendu) ou annoncee.

    Une SF compte comme suivie si sa date est passée, sinon elle est à venir (comptée « annoncée »).
    """
    if type_ == "SF":
        return "validee" if not quand or quand[:10] <= date.today().isoformat() else "annoncee"
    if statut in VALIDES:
        return "validee"
    s = statut.lower()
    if "annonce" in s or "complément" in s:
        return "annoncee"
    return "encours"


def sections(texte):
    """Découpe un export en fiches : (titre, {champ: valeur})."""
    fiches = []
    titre, champs = None, {}
    for ligne in texte.splitlines():
        if ligne.startswith("### "):
            if titre:
                fiches.append((titre, champs))
            titre, champs = ligne[4:].strip(), {}
        elif titre and ligne.startswith("- ") and " : " in ligne:
            cle, _, valeur = ligne[2:].partition(" : ")
            cle = cle.strip()
            if cle not in champs:
                champs[cle] = valeur.strip()
    if titre:
        fiches.append((titre, champs))
    return fiches


def numeros(valeur):
    """'12 . Leadership, 10. Communication' -> ['12', '10']."""
    return sorted({m.zfill(2) for m in re.findall(r"(?:^|,)\s*(\d{1,2})\s*\.", valeur)})


def corriger_trop_de_competences(valeur):
    """Corrige les fiches où presque toutes les compétences ont été cochées dans Notion.

    Quelques LI sont rattachées à 13 compétences, sans doute un « tout cocher »
    par erreur. Notion garde l'ordre dans lequel on a coché : les vraies
    compétences sont celles cochées avant la longue suite rangée dans l'ordre
    (02, 03, 04...). S'il n'y en a aucune avant, on garde la première.
    Renvoie (numéros gardés, True si corrigé).
    """
    ordre = []
    for m in re.findall(r"(?:^|,)\s*(\d{1,2})\s*\.", valeur):
        n = m.zfill(2)
        if n not in ordre:
            ordre.append(n)
    if len(ordre) < 10:
        return sorted(ordre), False
    debut = len(ordre) - 1
    while debut > 0 and ordre[debut - 1] < ordre[debut]:
        debut -= 1
    gardes = ordre[:debut] or ordre[:1]
    return sorted(gardes), True


def liens_notion():
    """Titre de page -> identifiant Notion, d'après le manifeste de l'export."""
    manifeste = json.loads((EXPORT / "manifest.json").read_text(encoding="utf-8"))
    liens = {}
    for ident, info in manifeste.items():
        liens.setdefault(info.get("title", "").strip(), ident.replace("-", ""))
    return liens


def construire():
    texte = (EXPORT / "competences.md").read_text(encoding="utf-8")
    competences = []
    for titre, champs in sections(texte):
        m = re.match(r"(\d{1,2})\s*\.\s*(.+)", titre)
        # Seulement les 14 compétences communes : la 15e est personnelle à chacun (décision de Léon du 2026-11-07)
        if m and int(m.group(1)) <= 14:
            competences.append({"id": "C" + m.group(1).zfill(2), "num": m.group(1).zfill(2), "nom": m.group(2).strip(),
                                "responsable": champs.get("Resp. Compétence", ""), "suppleant": champs.get("Suppléant", "")})

    liens = liens_notion()
    ressources = []
    for type_, fichier in SOURCES:
        for titre, champs in sections((EXPORT / fichier).read_text(encoding="utf-8")):
            valeur = champs.get("14 Compétences") or champs.get("14 compétences") or ""
            nums, corrige = corriger_trop_de_competences(valeur)
            nums = [n for n in nums if int(n) <= 14]
            if not nums:
                continue
            statut = champs.get("Statut", "")
            quand = champs.get("Date", "") or champs.get("Date J1", "")
            et = etape(type_, statut, quand)
            if type_ == "SF":
                statut = "Session suivie" if et == "validee" else "Session à venir"
            ressources.append({
                "id": f"{type_}{len(ressources)}",
                "type": type_,
                "titre": titre,
                "competences": ["C" + n for n in nums],
                "statut": statut,
                "etape": et,
                "valide": et == "validee",
                "semestre": champs.get("Semestre", ""),
                "date": quand,
                "format": champs.get("Type LI", ""),
                "notion": NOTION + liens[titre] if titre in liens else "",
                "corrige": corrige,
                # Qui l'a faite : auteurs d'une LI ou d'un AR, responsables d'une SF
                "experts": experts(champs.get("Expert·e", "")) if type_ == "SF" else [],
                "personnes": [p.strip() for p in (champs.get("Teampreneur") or champs.get("Responsables SF") or "").split(",") if p.strip()],
            })

    # SF prévues au calendrier de l'école mais pas encore dans Notion (sf-a-venir.json)
    fichier_sf = ICI / "sf-a-venir.json"
    if fichier_sf.exists():
        deja = {r["date"][:10] for r in ressources if r["type"] == "SF" and r["date"]}
        for sf in json.loads(fichier_sf.read_text(encoding="utf-8")).get("sessions", []):
            dates = sorted(sf["dates"])
            if deja & set(dates):
                continue
            et = etape("SF", "", dates[-1])
            ressources.append({
                "id": f"SF{len(ressources)}",
                "type": "SF",
                "titre": sf["titre"],
                "competences": ["C" + n for n in sf["competences"]],
                "statut": "Session suivie" if et == "validee" else "Session à venir",
                "etape": et,
                "valide": et == "validee",
                "semestre": "Semestre 3",
                "date": dates[0],
                "dates": dates,
                "format": "",
                "notion": "",
                "corrige": False,
                "experts": [],
                "personnes": [],
                "agenda": True,
            })

    # Date du dernier export (première ligne du journal de synchronisation)
    journal = (EXPORT / "journal.md").read_text(encoding="utf-8").splitlines()
    export = journal[0].replace("## ", "").strip() if journal else ""
    # Sous-compétences, à remplir avec les responsables de compétence (sous-competences.json)
    fichier_sous = ICI / "sous-competences.json"
    sous = json.loads(fichier_sous.read_text(encoding="utf-8")) if fichier_sous.exists() else {}
    sous = {k: v for k, v in sous.items() if k.startswith("C") and isinstance(v, list)}

    # Feuille de route de l'onglet Roadmap (roadmap.json)
    fichier_rm = ICI / "roadmap.json"
    roadmap = json.loads(fichier_rm.read_text(encoding="utf-8")).get("elements", []) if fichier_rm.exists() else []

    niveaux = lire_niveaux()
    exigences = cocher(ressources)
    # Combien de personnes visent chaque niveau (niveaux-vises.json, totaux seulement, sans noms)
    fichier_vises = ICI / "niveaux-vises.json"
    vises = json.loads(fichier_vises.read_text(encoding="utf-8")) if fichier_vises.exists() else {}
    vises = {k: v for k, v in vises.items() if k.startswith("C") and isinstance(v, dict)}
    # Contenu des fiches LI et AR (contenus.py) : critères des niveaux et recherche dans le contenu
    bruts = lire_contenus(ressources)
    fichiers = lire_fichiers(ressources)
    # Pour les critères : texte de la fiche + mots des fichiers joints (supports de SF, rendus de LI)
    criteres = rattacher_criteres(ressources, {r["id"]: sans_accents(bruts.get(r["id"], "")) + " " + fichiers.get(r["id"], {}).get("mots", "") for r in ressources})
    for r in ressources:
        # Le texte de la fiche, pour la recherche du site (« Gantt » trouvé même s'il n'est pas dans le titre, avec l'extrait)
        r["c"] = bruts.get(r["id"], "")
        # Les fichiers joints : leurs noms et leurs mots (sans le texte, qui appartient à leurs auteurs)
        if r["id"] in fichiers:
            r["fn"] = fichiers[r["id"]]["noms"]
            r["f"] = fichiers[r["id"]]["mots"]
    # Résumés faits par IA (resumes.json, clé = identifiant de la page Notion)
    fichier_res = ICI / "resumes.json"
    resumes = json.loads(fichier_res.read_text(encoding="utf-8")) if fichier_res.exists() else {}
    for r in ressources:
        g = re.search(r"([0-9a-f]{32})", r.get("notion") or "")
        if g:
            s = g.group(1)
            texte = resumes.get(f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}", "").strip()
            if texte:
                r["s"] = texte
    fichier_syn = ICI / "synonymes.json"
    synonymes = json.loads(fichier_syn.read_text(encoding="utf-8")).get("groupes", []) if fichier_syn.exists() else []
    return {"competences": competences, "ressources": ressources, "export": export, "sousCompetences": sous,
            "niveaux": niveaux, "exigences": exigences, "roadmap": roadmap, "vises": vises,
            "criteres": criteres, "synonymes": synonymes, "arbres": lire_arbres(ressources)}


def lire_arbres(ressources):
    """Les arbres de compétence (arbres.json) : pour chaque compétence, ses branches et les identifiants des ressources rangées dedans.

    Une ressource est désignée par un morceau de son titre (sans accents ni majuscules), suivi au besoin de « |date ».
    Les références introuvables sont signalées dans donnees-direct/verification-arbres.txt.
    """
    fichier = ICI / "arbres.json"
    if not fichier.exists():
        return {}
    source = json.loads(fichier.read_text(encoding="utf-8"))
    sortie, introuvables = {}, []
    for cid, branches in source.items():
        if not cid.startswith("C"):
            continue
        sortie[cid] = []
        for b in branches:
            ids = []
            for ref in b.get("r", []):
                morceau, _, date = ref.partition("|")
                trouvees = [r for r in ressources if sans_accents(morceau) in sans_accents(r["titre"])
                            and (not date or (r.get("date") or "").startswith(date))]
                if not trouvees:
                    introuvables.append(f"{cid} {b['n']} : {ref}")
                ids += [r["id"] for r in trouvees if r["id"] not in ids]
            sortie[cid].append({"n": b["n"], "d": b.get("d", ""), "niv": b.get("niv", []), "hors": bool(b.get("hors")), "res": ids})
    dossier = ICI / "donnees-direct"
    if dossier.exists():
        (dossier / "verification-arbres.txt").write_text("\n".join(introuvables) or "Tout est trouvé.", encoding="utf-8")
    return sortie


def lire_contenus(ressources):
    """Texte de chaque ressource (contenu de la fiche Notion, sans les passages qui citent les autres) : {id ressource : texte}."""
    fichier = ICI / "donnees-direct" / "contenus.json"
    brut = json.loads(fichier.read_text(encoding="utf-8")) if fichier.exists() else {}
    manifeste = json.loads((EXPORT / "manifest.json").read_text(encoding="utf-8"))
    par_titre = {}
    for ident, info in manifeste.items():
        if ident in brut:
            par_titre.setdefault(info.get("title", "").strip(), brut[ident])
    return {r["id"]: unicodedata.normalize("NFC", par_titre.get(r["titre"], "")) for r in ressources}


def lire_fichiers(ressources):
    """Noms et mots des fichiers joints à chaque ressource (contenus-fichiers.json, fait par fichiers.py)."""
    fichier = ICI / "contenus-fichiers.json"
    brut = json.loads(fichier.read_text(encoding="utf-8")) if fichier.exists() else {}
    manifeste = json.loads((EXPORT / "manifest.json").read_text(encoding="utf-8"))
    par_titre = {}
    for ident, info in manifeste.items():
        if ident in brut:
            par_titre.setdefault(info.get("title", "").strip(), brut[ident])
    return {r["id"]: par_titre[r["titre"]] for r in ressources if r["titre"] in par_titre}


def compte(mot, texte):
    """Nombre de fois où le mot-clé apparaît dans un texte déjà sans accents (début de mot)."""
    return len(re.findall(r"(?<![a-z0-9])" + re.escape(sans_accents(mot)), texte))


def rattacher_criteres(ressources, contenus):
    """Pour chaque critère des niveaux visés (criteres.json), les ressources qui en parlent.

    Gardée : une ressource dont le titre contient un mot-clé, ou dont le contenu en parle
    au moins 2 fois (si elle est rattachée à la compétence) ou au moins 5 fois (sinon).
    Les mots-clés de 3 lettres ou moins ne sont cherchés que dans les titres (« ai », « roi »).
    """
    fichier = ICI / "criteres.json"
    if not fichier.exists():
        return {}
    source = json.loads(fichier.read_text(encoding="utf-8"))
    sortie = {}
    for cid, par_niveau in source.items():
        if not cid.startswith("C"):
            continue
        sortie[cid] = {}
        for niv, criteres in par_niveau.items():
            liste = []
            for cr in criteres:
                gardees = []
                for r in ressources:
                    kw = cr.get("kw", [])
                    titre = any(cherche(k, r["titre"]) for k in kw)
                    n = sum(compte(k, contenus.get(r["id"], "")) for k in kw if len(k) > 3)
                    seuil = 2 if cid in r["competences"] else 5
                    if titre or n >= seuil:
                        gardees.append((not r["valide"], -(100 if titre else 0) - n, r["id"]))
                gardees.sort()
                # kw : utilisés aussi par « Vérifier une idée » sur le site
                liste.append({"t": cr["t"], "kw": cr.get("kw", []), "res": [g[2] for g in gardees]})
            sortie[cid][niv] = liste
    return sortie


def lire_niveaux():
    """Texte des 5 niveaux de chaque compétence, tiré du référentiel officiel : {'C01': [{num, nom, texte}, ...]}."""
    if not REFERENTIEL.exists():
        return {}
    niveaux, cid, courant = {}, None, None
    for ligne in REFERENTIEL.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### Compétence (\d+)", ligne)
        if m:
            cid = "C" + m.group(1).zfill(2)
            niveaux[cid], courant = [], None
            continue
        if ligne.startswith("## "):
            cid, courant = None, None
            continue
        m = re.match(r"\*\*Niveau (\d), (.+)\*\*", ligne)
        if cid and m:
            courant = {"num": int(m.group(1)), "nom": m.group(2).strip(), "texte": ""}
            niveaux[cid].append(courant)
            continue
        texte = ligne.lstrip("> ").strip()
        if courant is not None and texte and not courant["texte"]:
            courant["texte"] = texte
    return niveaux


def sans_accents(s):
    s = unicodedata.normalize("NFD", s.replace("’", "'"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def cherche(mot, titre):
    """Le mot-clé apparaît-il dans le titre, en début de mot (et en mot entier s'il est court) ?"""
    motif = r"(?<![a-z0-9])" + re.escape(sans_accents(mot)) + (r"(?![a-z0-9])" if len(mot) <= 3 else "")
    return re.search(motif, sans_accents(titre)) is not None


def cocher(ressources):
    """Pour chaque élément de théorie exigé (exigences.json), les ressources de l'équipe qui le couvrent.

    État : couvert (au moins une ressource validée), encours (seulement des ressources pas encore validées),
    vide (rien), preuve (à prouver soi-même, ne se voit pas dans un titre).
    """
    fichier = ICI / "exigences.json"
    if not fichier.exists():
        return {}
    source = json.loads(fichier.read_text(encoding="utf-8"))
    sortie = {}
    for cid, par_niveau in source.items():
        if not cid.startswith("C"):
            continue
        sortie[cid] = {}
        for niv, elements in par_niveau.items():
            liste = []
            for el in elements:
                trouvees = []
                if el.get("preuve"):
                    etat = "preuve"
                else:
                    for r in ressources:
                        dans_comp = cid in r["competences"]
                        if el.get("type"):
                            ok = dans_comp and r["type"] == el["type"]
                        else:
                            ok = (dans_comp or el.get("partout")) and any(cherche(k, r["titre"]) for k in el.get("kw", []))
                        if ok:
                            trouvees.append(r)
                    trouvees.sort(key=lambda r: (not r["valide"], r["titre"]))
                    etat = "couvert" if any(r["valide"] for r in trouvees) else "encours" if trouvees else "vide"
                liste.append({"t": el["t"], "exige": bool(el.get("exige")), "etat": etat, "res": [r["id"] for r in trouvees]})
            sortie[cid][niv] = liste
    return sortie


def main():
    donnees = construire()
    gabarit = (ICI / "template.html").read_text(encoding="utf-8")
    page = gabarit.replace("/*DONNEES*/null", json.dumps(donnees, ensure_ascii=False))
    # Mesure d'audience Microsoft Clarity : active seulement si clarity.txt contient l'identifiant du projet
    fichier_clarity = ICI / "clarity.txt"
    id_clarity = fichier_clarity.read_text(encoding="utf-8").strip() if fichier_clarity.exists() else ""
    script_clarity = ""
    if id_clarity:
        script_clarity = ('<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};'
                          't=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;'
                          'y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})'
                          '(window,document,"clarity","script","' + id_clarity + '");</script>')
    page = page.replace("<!--CLARITY-->", script_clarity)
    (ICI / "index.html").write_text(page, encoding="utf-8")
    par_type = {}
    for r in donnees["ressources"]:
        par_type[r["type"]] = par_type.get(r["type"], 0) + 1
    print(f"{len(donnees['competences'])} compétences, ressources : {par_type}")
    # Relecture : pour chaque élément de théorie, ce qui a été trouvé (à vérifier à la main)
    titres = {r["id"]: ("" if r["valide"] else "[en cours] ") + r["titre"] for r in donnees["ressources"]}
    with open(ICI / "donnees-direct" / "verification-exigences.txt", "w", encoding="utf-8") as f:
        for cid, par_niveau in donnees["exigences"].items():
            for niv, elements in par_niveau.items():
                for el in elements:
                    f.write(f"{cid} N{niv} [{el['etat']}] {el['t']}\n")
                    for i in el["res"]:
                        f.write(f"      - {titres[i]}\n")


if __name__ == "__main__":
    main()
