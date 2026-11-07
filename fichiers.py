"""Lit le texte des fichiers joints aux fiches LI, AR et SF du Notion public de Sedniner (lecture seule).

Les fichiers (PDF, PowerPoint, Word) sont téléchargés dans donnees-direct/fichiers/ (jamais envoyés
en ligne), puis leur texte est réduit à une liste de mots sans doublons, rangée dans
contenus-fichiers.json : {identifiant de la fiche : {"noms": [fichiers], "mots": "..."}}.
Ce fichier-là est envoyé sur GitHub pour que la mise à jour du lundi le garde ; il ne contient
que des mots isolés, pas le texte des supports (qui appartient à leurs auteurs).

Les images et les PDF scannés (sans texte) sont ignorés pour l'instant.
Lancer : python fichiers.py (seuls les nouveaux fichiers sont téléchargés), puis python build.py.
"""

import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
from notion_api import load_page, val, post, UA  # noqa: E402

DOSSIER = ICI / "donnees-direct" / "fichiers"
SORTIE = ICI / "contenus-fichiers.json"
BASES = ["lectures-individuelles-li.md", "articles-reflexifs-ar.md", "sessions-de-formation-sf.md"]
EXTENSIONS = (".pdf", ".pptx", ".docx")


def ids_a_lire():
    manifeste = json.loads((ICI / "donnees-direct" / "manifest.json").read_text(encoding="utf-8"))
    titres = set()
    for f in BASES:
        for ligne in (ICI / "donnees-direct" / f).read_text(encoding="utf-8").splitlines():
            if ligne.startswith("### "):
                titres.add(ligne[4:].strip())
    return [i for i, m in manifeste.items() if m.get("title", "").strip() in titres]


def pieces_jointes(pid):
    """(bloc, adresse attachment:, nom) de chaque fichier de la fiche : blocs fichier/PDF et champs fichier."""
    blocs, _ = load_page(pid)
    trouvees = []
    for k, b in blocs.items():
        v = val(b)
        props = v.get("properties") or {}
        if v.get("type") in ("file", "pdf"):
            src = ((props.get("source") or [[""]])[0] or [""])[0]
            nom = "".join(s[0] for s in props.get("title") or [] if s and isinstance(s[0], str)) or src.rsplit(":", 1)[-1]
            if src.startswith("attachment:"):
                trouvees.append((k, src, nom, v.get("space_id")))
        if k == pid:
            # Champs « fichier » de la fiche (par exemple « Dépôt LI »)
            for segs in props.values():
                for s in segs or []:
                    for f in (s[1] if len(s) > 1 else []):
                        if f and f[0] == "a" and str(f[1]).startswith("attachment:"):
                            trouvees.append((k, f[1], s[0], v.get("space_id")))
    return [t for t in trouvees if t[2].lower().endswith(EXTENSIONS)]


def telecharger(bloc, src, espace, cible):
    d = post("getSignedFileUrls", {"urls": [{"url": src, "permissionRecord": {"table": "block", "id": bloc, "spaceId": espace}}]})
    url = (d.get("signedUrls") or [None])[0]
    if not url:
        raise RuntimeError("pas d'adresse de téléchargement")
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
        cible.write_bytes(r.read())


def texte_du_fichier(chemin):
    ext = chemin.suffix.lower()
    if ext == ".pdf":
        import pymupdf
        with pymupdf.open(chemin) as doc:
            return " ".join(p.get_text() for p in doc)
    if ext == ".pptx":
        from pptx import Presentation
        morceaux = []
        for diapo in Presentation(chemin).slides:
            for forme in diapo.shapes:
                if forme.has_text_frame:
                    morceaux.append(forme.text_frame.text)
            if diapo.has_notes_slide:
                morceaux.append(diapo.notes_slide.notes_text_frame.text)
        return " ".join(morceaux)
    if ext == ".docx":
        import docx
        return " ".join(p.text for p in docx.Document(chemin).paragraphs)
    return ""


def mots(texte):
    s = unicodedata.normalize("NFD", texte.replace("’", "'"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return " ".join(sorted(set(w for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", s) if len(w) >= 3)))


def main():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    sortie = json.loads(SORTIE.read_text(encoding="utf-8")) if SORTIE.exists() else {}
    ids = ids_a_lire()
    lus = 0
    for n, pid in enumerate(ids, 1):
        try:
            pj = pieces_jointes(pid)
        except Exception as e:
            print("échec fiche", pid, e)
            continue
        noms, textes = [], []
        for bloc, src, nom, espace in pj:
            ext = Path(nom).suffix.lower()
            cible = DOSSIER / (src.split(":")[1] + ext)
            try:
                if not cible.exists():
                    telecharger(bloc, src, espace, cible)
                    lus += 1
                    time.sleep(0.3)
                textes.append(texte_du_fichier(cible))
                noms.append(nom)
            except Exception as e:
                print("échec fichier", nom, e)
        if noms:
            sortie[pid] = {"noms": noms, "mots": mots(" ".join(textes))}
        else:
            sortie.pop(pid, None)
        if n % 25 == 0:
            print(f"{n}/{len(ids)} fiches, {lus} fichiers téléchargés")
            SORTIE.write_text(json.dumps(sortie, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.2)
    SORTIE.write_text(json.dumps(sortie, ensure_ascii=False), encoding="utf-8")
    vides = sum(1 for v in sortie.values() if not v["mots"])
    print(f"{len(sortie)} fiches avec fichiers ({vides} sans texte lisible, sans doute scannés), {lus} téléchargés cette fois")


if __name__ == "__main__":
    main()
