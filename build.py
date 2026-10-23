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
REFERENTIEL = ICI.parents[2] / "bta" / "team-academy" / "Référentiel 14 compétences 2024 - 2025.md"

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
        if m:
            competences.append({"id": "C" + m.group(1).zfill(2), "num": m.group(1).zfill(2), "nom": m.group(2).strip(),
                                "responsable": champs.get("Resp. Compétence", ""), "suppleant": champs.get("Suppléant", "")})

    liens = liens_notion()
    ressources = []
    for type_, fichier in SOURCES:
        for titre, champs in sections((EXPORT / fichier).read_text(encoding="utf-8")):
            valeur = champs.get("14 Compétences") or champs.get("14 compétences") or ""
            nums, corrige = corriger_trop_de_competences(valeur)
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
                "personnes": [p.strip() for p in (champs.get("Teampreneur") or champs.get("Responsables SF") or "").split(",") if p.strip()],
            })

    # Date du dernier export (première ligne du journal de synchronisation)
    journal = (EXPORT / "journal.md").read_text(encoding="utf-8").splitlines()
    export = journal[0].replace("## ", "").strip() if journal else ""
    # Sous-compétences, à remplir avec les responsables de compétence (sous-competences.json)
    fichier_sous = ICI / "sous-competences.json"
    sous = json.loads(fichier_sous.read_text(encoding="utf-8")) if fichier_sous.exists() else {}
    sous = {k: v for k, v in sous.items() if k.startswith("C") and isinstance(v, list)}

    niveaux = lire_niveaux()
    exigences = cocher(ressources)
    return {"competences": competences, "ressources": ressources, "export": export, "sousCompetences": sous,
            "niveaux": niveaux, "exigences": exigences}


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
