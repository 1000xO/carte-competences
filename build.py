"""Génère le site « carte des compétences » à partir de l'export Notion Sedniner.

Lit les fichiers Markdown de 04 PROJET/bta/team-academy/notion-sedniner/
(LI, AR, SF, compétences), en tire les ressources et leurs compétences,
puis remplit template.html pour produire index.html (un seul fichier, à
ouvrir dans le navigateur).

Lancer : python build.py
"""

import json
import re
from pathlib import Path

ICI = Path(__file__).resolve().parent
EXPORT = ICI.parents[2] / "bta" / "team-academy" / "notion-sedniner"
# Si la lecture directe des 4 bases a été faite (notion_direct.py), on part de là : c'est plus récent
if (ICI / "donnees-direct" / "competences.md").exists():
    EXPORT = ICI / "donnees-direct"
NOTION = "https://chief-zinnia-fe9.notion.site/"

SOURCES = [
    ("LI", "lectures-individuelles-li.md"),
    ("AR", "articles-reflexifs-ar.md"),
    ("SF", "sessions-de-formation-sf.md"),
]

# Statuts considérés comme « validés » (ressource terminée et acceptée)
VALIDES = {"LI Validée", "AR Validé"}


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
    for titre, _ in sections(texte):
        m = re.match(r"(\d{1,2})\s*\.\s*(.+)", titre)
        if m:
            competences.append({"id": "C" + m.group(1).zfill(2), "num": m.group(1).zfill(2), "nom": m.group(2).strip()})

    liens = liens_notion()
    ressources = []
    for type_, fichier in SOURCES:
        for titre, champs in sections((EXPORT / fichier).read_text(encoding="utf-8")):
            valeur = champs.get("14 Compétences") or champs.get("14 compétences") or ""
            nums, corrige = corriger_trop_de_competences(valeur)
            if not nums:
                continue
            statut = champs.get("Statut", "")
            ressources.append({
                "id": f"{type_}{len(ressources)}",
                "type": type_,
                "titre": titre,
                "competences": ["C" + n for n in nums],
                "statut": statut or ("Session" if type_ == "SF" else ""),
                "valide": statut in VALIDES or type_ == "SF",
                "semestre": champs.get("Semestre", ""),
                "date": champs.get("Date", "") or champs.get("Date J1", ""),
                "format": champs.get("Type LI", ""),
                "notion": NOTION + liens[titre] if titre in liens else "",
                "corrige": corrige,
            })

    # Date du dernier export (première ligne du journal de synchronisation)
    journal = (EXPORT / "journal.md").read_text(encoding="utf-8").splitlines()
    export = journal[0].replace("## ", "").strip() if journal else ""
    # Sous-compétences, à remplir avec les responsables de compétence (sous-competences.json)
    fichier_sous = ICI / "sous-competences.json"
    sous = json.loads(fichier_sous.read_text(encoding="utf-8")) if fichier_sous.exists() else {}
    sous = {k: v for k, v in sous.items() if k.startswith("C") and isinstance(v, list)}

    return {"competences": competences, "ressources": ressources, "export": export, "sousCompetences": sous}


def main():
    donnees = construire()
    gabarit = (ICI / "template.html").read_text(encoding="utf-8")
    page = gabarit.replace("/*DONNEES*/null", json.dumps(donnees, ensure_ascii=False))
    (ICI / "index.html").write_text(page, encoding="utf-8")
    par_type = {}
    for r in donnees["ressources"]:
        par_type[r["type"]] = par_type.get(r["type"], 0) + 1
    print(f"{len(donnees['competences'])} compétences, ressources : {par_type}")


if __name__ == "__main__":
    main()
