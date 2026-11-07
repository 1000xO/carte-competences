"""Récupère le texte de chaque fiche LI, AR et SF du Notion public de Sedniner (lecture seule).

Sert à deux choses sur le site : rattacher les ressources aux critères des niveaux,
et chercher un outil (« Gantt ») dans le contenu, pas seulement dans les titres.

Écrit donnees-direct/contenus.json : {identifiant de la fiche : texte}.
Lancer après notion_direct.py : python contenus.py, puis python build.py.
Une fiche déjà lue n'est relue que si on lance : python contenus.py --tout
"""

import json
import sys
import time
from pathlib import Path

ICI = Path(__file__).resolve().parent
from notion_api import load_page, val  # noqa: E402

SORTIE = ICI / "donnees-direct" / "contenus.json"
FICHIERS = ["lectures-individuelles-li.md", "articles-reflexifs-ar.md", "sessions-de-formation-sf.md"]


def ids_a_lire():
    """Les identifiants des fiches LI et AR, dans l'ordre du manifeste, d'après les titres des deux fichiers."""
    manifeste = json.loads((ICI / "donnees-direct" / "manifest.json").read_text(encoding="utf-8"))
    titres = set()
    for f in FICHIERS:
        for ligne in (ICI / "donnees-direct" / f).read_text(encoding="utf-8").splitlines():
            if ligne.startswith("### "):
                titres.add(ligne[4:].strip())
    return [i for i, m in manifeste.items() if m.get("title", "").strip() in titres]


# Questions du modèle d'annonce dont la réponse cite les lectures des AUTRES : on saute la question
# et sa réponse, sinon une LI qui cite « SF Gestion de projet : GANTT » serait trouvée pour « Gantt ».
A_SAUTER = ("quelles sont les lectures", "quels sont les lectures", "en quoi cette lecture", "en quoi cet article",
            "d'ou vient ce livre", "s'agit-il d", "s'il s'agit d", "ne pas oublier de completer")
# Questions du modèle dont on garde la réponse, mais pas le texte de la question
MODELE = ("pourquoi souhaitez-vous", "table des matieres", "au minimum 4 sources", "quel est le questionnement")


def _norm(s):
    import unicodedata
    s = unicodedata.normalize("NFD", s.replace("’", "'"))
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").lower().split())


def texte_de_page(pid):
    """Texte de la fiche dans l'ordre de la page, sans les passages qui citent les ressources des autres."""
    blocs, _ = load_page(pid)
    ordre = []

    def parcours(i, prof):
        v = val(blocs.get(i, {}))
        if i != pid:
            if v.get("type") in ("collection_view", "collection_view_page"):
                return
            t = "".join(s[0] for s in (v.get("properties") or {}).get("title") or [] if s and isinstance(s[0], str))
            ordre.append((prof, v.get("type", ""), t))
        for c in v.get("content") or []:
            if c in blocs:
                parcours(c, prof + 1)

    parcours(pid, 0)
    morceaux, saut = [], None  # saut = profondeur de la question en cours de saut
    for prof, typ, t in ordre:
        n = _norm(t)
        if saut is not None:
            # On reste dans le saut pour les sous-blocs et les paragraphes de réponse au même niveau
            if prof > saut or (prof == saut and typ == "text"):
                continue
            saut = None
        if n.startswith(A_SAUTER):
            saut = prof
            continue
        if n.startswith(MODELE):
            continue
        if t.strip():
            morceaux.append(t)
    return " ".join(" ".join(morceaux).split())


def main():
    tout = "--tout" in sys.argv
    deja = json.loads(SORTIE.read_text(encoding="utf-8")) if SORTIE.exists() else {}
    ids = ids_a_lire()
    lus = 0
    for n, pid in enumerate(ids, 1):
        if pid in deja and not tout:
            continue
        try:
            deja[pid] = texte_de_page(pid)
            lus += 1
        except Exception as e:
            print("échec", pid, e)
        if lus % 20 == 0:
            SORTIE.write_text(json.dumps(deja, ensure_ascii=False), encoding="utf-8")
            print(f"{n}/{len(ids)}")
        time.sleep(0.2)
    deja = {k: v for k, v in deja.items() if k in set(ids)}
    SORTIE.write_text(json.dumps(deja, ensure_ascii=False), encoding="utf-8")
    print(f"{len(deja)} fiches avec contenu, {lus} lues cette fois")


if __name__ == "__main__":
    main()
