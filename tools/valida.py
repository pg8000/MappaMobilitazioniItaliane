#!/usr/bin/env python3
"""Controlla data/eventi.json: campi obbligatori, chiavi esistenti, date, fonti. Esce con errore se qualcosa non va."""
import re, sys, datetime as dt
from comuni import carica, province

TIPI, AMBITI = {"sciopero", "manifestazione"}, {"locale", "regionale", "nazionale", "multiregionale"}
OBBL = ["id", "type", "scope", "sector", "start", "end", "title", "who", "orgs", "src"]


def errori_evento(e, base, luoghi=None):
    err = []
    luoghi = luoghi if luoghi is not None else base["luoghi"]
    for k in OBBL:
        if not e.get(k):
            err.append(f"campo mancante: {k}")
    if err:
        return err
    if e["type"] not in TIPI:
        err.append(f"type non valido: {e['type']}")
    if e["scope"] not in AMBITI:
        err.append(f"scope non valido: {e['scope']}")
    for k in ("start", "end"):
        try:
            dt.date.fromisoformat(e[k])
        except ValueError:
            err.append(f"{k} non è una data ISO (AAAA-MM-GG): {e[k]}")
    if not err and e["end"] < e["start"]:
        err.append("end precede start")
    if not err and (e["end"] < "2026-01-01" or e["start"] > "2026-12-31"):
        err.append("evento fuori dal 2026")
    if e.get("place") and e["place"] not in luoghi:
        err.append(f"place sconosciuto: {e['place']}")
    if not e.get("place") and e["scope"] in ("locale",):
        err.append("un evento locale ha bisogno di place")
    for o in e["orgs"]:
        if o not in base["promotori"]:
            err.append(f"promotore sconosciuto: {o}")
    for s in e["src"]:
        if s not in base["fonti"]:
            err.append(f"fonte sconosciuta: {s}")
    if "exc" in e and not (e["exc"].get("kind") and e["exc"].get("note")):
        err.append("exc richiede kind e note")
    for k in ("title", "who", "time", "where", "area", "sector"):
        v = str(e.get(k, ""))
        if "DA COMPILARE" in v.upper() or len(v) > 300:
            err.append(f"{k}: testo incompleto o troppo lungo")
    return err


def main():
    base = carica("eventi.json")
    ids, tot = set(), 0
    for e in base["eventi"]:
        if e.get("id") in ids:
            print("id duplicato:", e["id"]); tot += 1
        ids.add(e.get("id"))
        for m in errori_evento(e, base):
            print(f"[{e.get('id')}] {m}"); tot += 1
    for k, f in base["fonti"].items():
        if not str(f.get("url", "")).startswith("https://"):
            print(f"fonte {k}: url non https"); tot += 1
    if tot:
        sys.exit(f"{tot} problemi in data/eventi.json")
    print(f"eventi.json ok: {len(base['eventi'])} eventi")
    if "--archivio" in sys.argv:
        archive = carica("archivio.json")
        ids = set()
        for e in archive["eventi"]:
            if e["id"] in ids:
                sys.exit("ID duplicato nell'archivio")
            ids.add(e["id"])
            for key in ("start", "end"):
                dt.date.fromisoformat(e[key])
            if e["start"] > e["end"] or e["end"] < "2026-01-01" or e["start"] > "2026-12-31":
                sys.exit(f"Date fuori archivio: {e['id']}")
            if not e.get("src") or any(k not in archive["fonti"] for k in e["src"]):
                sys.exit(f"Fonte assente: {e['id']}")
            if any(k not in archive["promotori"] for k in e["orgs"]):
                sys.exit(f"Promotore sconosciuto: {e['id']}")
            if e.get("place") and e["place"] not in archive["luoghi"]:
                sys.exit(f"Luogo sconosciuto: {e['id']}")
        print(f"archivio.json ok: {len(ids)} voci, fonti e riferimenti validi")


if __name__ == "__main__":
    main()
