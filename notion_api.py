"""Appels en lecture seule au Notion public de Sedniner.

Copie des quelques fonctions de 04 PROJET/bta/team-academy/notion-sedniner/sync.py
dont notion_direct.py a besoin, pour que le site se mette à jour tout seul
sur GitHub (où le reste du classeur n'existe pas).
"""

import json
import time
import urllib.request

HOST = "https://chief-zinnia-fe9.notion.site/api/v3/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

EXCLUDE = {
    "28ef31e1-1ebc-80ef-96c6-d5c9219f38f5",  # 24h client
    "2b1f31e1-1ebc-80ec-b30e-c60d44a08ef0",  # Finances
    "35ff31e1-1ebc-8084-91f4-ef00ed0609a4",  # Business Meeting
}


def post(ep, body):
    # Jusqu'à 4 essais espacés : une coupure internet de quelques minutes ne doit pas gâcher le passage
    for essai in range(4):
        try:
            r = urllib.request.Request(HOST + ep, data=json.dumps(body).encode(),
                                       headers={"Content-Type": "application/json", "User-Agent": UA})
            return json.load(urllib.request.urlopen(r, timeout=60))
        except Exception:
            if essai == 3:
                raise
            time.sleep(30 * (essai + 1))


def load_page(pid):
    blocks, cols, cursor, n = {}, {}, {"stack": []}, 0
    while True:
        d = post("loadPageChunk", {"page": {"id": pid}, "limit": 100, "cursor": cursor,
                                   "chunkNumber": n, "verticalColumns": False})
        rm = d["recordMap"]
        blocks.update(rm.get("block", {}))
        cols.update(rm.get("collection", {}))
        cursor = d.get("cursor", {"stack": []})
        n += 1
        if not cursor.get("stack") or n > 60:
            break
    return blocks, cols


def val(b):
    v = b.get("value", {})
    return v.get("value", v)
