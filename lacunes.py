"""Calcule les lacunes de l'équipe par compétence, à partir de l'export Notion Sedniner.

Réutilise la lecture de build.py (mêmes ressources, mêmes règles de validation)
et écrit ../lacunes-par-competence.md : pour chaque compétence, le nombre de
LI et d'AR validés, de SF, et la liste des titres (utile pour transmettre au
prof-expert ce que l'équipe a déjà fait sur un thème de SF).

Lancer : python lacunes.py (après python build.py, ou seul)
"""

from datetime import date
from build import construire, EXPORT, sections

SORTIE = __import__("pathlib").Path(__file__).resolve().parent.parent / "lacunes-par-competence.md"


def main():
    donnees = construire()
    comps = donnees["competences"]
    # Une ressource rattachée à 13 compétences ou plus ne dit rien d'une compétence précise :
    # même règle que le site, on l'écarte des comptes.
    ressources = [r for r in donnees["ressources"] if len(r["competences"]) < 13]
    ecartees = len(donnees["ressources"]) - len(ressources)

    lignes = []
    for c in comps:
        rs = [r for r in ressources if c["id"] in r["competences"]]
        li = [r for r in rs if r["type"] == "LI" and r["valide"]]
        ar = [r for r in rs if r["type"] == "AR" and r["valide"]]
        sf = [r for r in rs if r["type"] == "SF"]
        lignes.append({"c": c, "li": li, "ar": ar, "sf": sf, "total": len(li) + len(ar) + len(sf)})

    lignes.sort(key=lambda l: (l["total"], len(l["sf"])))
    manifeste_date = (EXPORT / "journal.md").read_text(encoding="utf-8").split("\n", 1)[0].replace("## ", "")

    out = []
    out.append("Origine : calcul automatique (`site/lacunes.py`) à partir de l'export Notion Sedniner (`04 PROJET/bta/team-academy/notion-sedniner/`).")
    out.append(f"Date : {date.today().isoformat()}, export du {manifeste_date}.")
    out.append("Usage : voir où l'équipe a le moins appris, compétence par compétence, pour choisir les prochaines SF. Livrable L1 de l'atterrissage de la LI.")
    out.append("")
    out.append("# Les lacunes de l'équipe, compétence par compétence")
    out.append("")
    out.append("Compté : les LI et AR au statut validé, et toutes les SF, rattachées à la compétence dans Notion. Classé de la compétence la moins nourrie à la plus nourrie. " + (f"{ecartees} ressources rattachées à 13 compétences ou plus sont écartées, car elles ne disent rien d'une compétence précise." if ecartees else ""))
    out.append("")
    out.append("| Compétence | LI validées | AR validés | SF | Total |")
    out.append("|---|---|---|---|---|")
    for l in lignes:
        out.append(f"| {l['c']['num']}. {l['c']['nom']} | {len(l['li'])} | {len(l['ar'])} | {len(l['sf'])} | {l['total']} |")
    out.append("")
    out.append("## Le détail, compétence par compétence")
    out.append("")
    for l in lignes:
        out.append(f"### {l['c']['num']}. {l['c']['nom']}")
        out.append("")
        for libelle, liste in (("SF", l["sf"]), ("LI validées", l["li"]), ("AR validés", l["ar"])):
            titres = sorted({r["titre"] for r in liste})
            out.append(f"- **{libelle}** ({len(titres)}) : " + ("; ".join(titres) if titres else "aucune"))
        out.append("")
    SORTIE.write_text("\n".join(out), encoding="utf-8")
    print(f"Écrit : {SORTIE}")
    for l in lignes[:5]:
        print(l["c"]["num"], l["c"]["nom"], len(l["li"]), len(l["ar"]), len(l["sf"]))


if __name__ == "__main__":
    main()
