"""Récupère en direct, depuis le Notion public de Sedniner, les 4 bases utiles au site.

Plus rapide que l'export complet (notion-sedniner/sync.py, environ 3 300 pages
lues une par une) : on ne lit que les bases LI, AR, SF et Compétences, avec
les champs de chaque fiche (pas le contenu des pages). Lecture seule.

Écrit dans donnees-direct/ des fichiers au même format que l'export
(### titre, puis « - Champ : valeur »), plus manifest.json et journal.md.
build.py lit ce dossier en priorité s'il existe.

Lancer : python notion_direct.py, puis python build.py
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parents[2] / "bta" / "team-academy" / "notion-sedniner"))
from sync import post, load_page, val, EXCLUDE  # noqa: E402  (mêmes appels que l'export complet)

SORTIE = ICI / "donnees-direct"
# Le Notion public cache les noms des personnes (Teampreneur) : on les prend dans
# personnes.json, relevé à la main depuis une session Notion connectée
PERSONNES = json.loads((ICI / "personnes.json").read_text(encoding="utf-8")) if (ICI / "personnes.json").exists() else {}
BASES = [
    ("Lectures individuelles (LI)", "bc2bcbb1-0743-4f75-a4f9-6cb683eaf610", "lectures-individuelles-li.md"),
    ("Articles reflexifs (AR)", "2ce94ed4-5c44-4d7e-a46d-17782ef50aa3", "articles-reflexifs-ar.md"),
    ("Sessions de formation (SF)", "6b0811b1-2a12-43a7-a257-cdef465fdc6a", "sessions-de-formation-sf.md"),
    ("Competences", "d9c2be0d-daa1-4a13-9ddd-a7bcb9e8ea1c", "competences.md"),
]


def collection_views(pid, profondeur=2):
    """Les bases (collection_view) d'une page, en descendant dans ses sous-pages si besoin."""
    blocs, _ = load_page(pid)
    trouvees, sous_pages = [], []
    for k, b in blocs.items():
        v = val(b)
        if v.get("type") in ("collection_view", "collection_view_page") and k not in EXCLUDE:
            trouvees.append(v | {"id": k})
        elif v.get("type") == "page" and k != pid:
            sous_pages.append(k)
    if not trouvees and profondeur > 0:
        for sp in sous_pages[:10]:
            trouvees += collection_views(sp, profondeur - 1)
    return trouvees


def lire_base(v):
    cp = v.get("format", {}).get("collection_pointer") or {}
    cid = cp.get("id") or v.get("collection_id")
    sp = cp.get("spaceId") or v.get("space_id")
    vues = v.get("view_ids") or []
    if not cid or not vues:
        return None
    d = post("queryCollection", {
        "collection": {"id": cid, "spaceId": sp},
        "collectionView": {"id": vues[0], "spaceId": sp},
        "loader": {"type": "reducer", "reducers": {"collection_group_results": {"type": "results", "limit": 2000}},
                   "searchQuery": "", "userTimeZone": "Europe/Zurich"},
    })
    ids = d.get("result", {}).get("reducerResults", {}).get("collection_group_results", {}).get("blockIds", [])
    rm = d.get("recordMap", {})
    col = val(rm.get("collection", {}).get(cid, {}))
    return {"ids": ids, "blocs": rm.get("block", {}), "schema": col.get("schema", {})}


def texte(segs, noms):
    o = ""
    for s in segs or []:
        t = s[0]
        for f in (s[1] if len(s) > 1 else []):
            if f[0] == "p":
                t = noms.get(f[1], "page liee")
            elif f[0] == "u":
                t = PERSONNES.get(f[1], "")
            elif f[0] == "d":
                dv = f[1]
                t = dv.get("start_date", "") + (" -> " + dv["end_date"] if dv.get("end_date") else "")
        o += t
    return o


def main():
    SORTIE.mkdir(exist_ok=True)
    bases = {}
    for nom, racine, fichier in BASES:
        vues = collection_views(racine)
        lues = [b for b in (lire_base(v) for v in vues) if b]
        # La base principale est celle qui a le plus de fiches
        bases[fichier] = (nom, max(lues, key=lambda b: len(b["ids"])) if lues else None)
        time.sleep(0.2)

    # Titres de toutes les fiches, pour remplacer les liens (« ‣ ») par des noms
    noms, manifeste = {}, {}
    for _, b in bases.values():
        if not b:
            continue
        for i in b["ids"]:
            v = val(b["blocs"].get(i, {}))
            t = texte((v.get("properties") or {}).get("title"), {})
            noms[i] = t
            manifeste[i] = {"title": t}

    total = {}
    for fichier, (nom, b) in bases.items():
        lignes = [f"# {nom}", ""]
        if b:
            for i in b["ids"]:
                v = val(b["blocs"].get(i, {}))
                props = v.get("properties") or {}
                lignes.append("### " + noms.get(i, ""))
                lignes.append("")
                for pid, sc in b["schema"].items():
                    if sc.get("type") == "title" or pid not in props:
                        continue
                    s = texte(props[pid], noms).strip()
                    if s:
                        lignes.append(f"- {sc['name']} : {s}")
                lignes.append("")
        (SORTIE / fichier).write_text("\n".join(lignes), encoding="utf-8")
        total[nom] = len(b["ids"]) if b else 0

    (SORTIE / "manifest.json").write_text(json.dumps(manifeste, ensure_ascii=False), encoding="utf-8")
    (SORTIE / "journal.md").write_text(f"## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nLecture directe des bases LI, AR, SF et Compétences.\n", encoding="utf-8")
    print(total)


if __name__ == "__main__":
    main()
