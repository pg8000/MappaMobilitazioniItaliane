"""Archivio unico: proclamazioni MIT autorevoli e iniziative curate a mano."""
from comuni import carica, DATA


def unisci():
    base = carica("eventi.json")
    mit = carica("scioperi-mit.json") if (DATA / "scioperi-mit.json").exists() else {}
    official = mit.get("eventi", [])
    # Le vecchie schede manuali MIT erano un riassunto di singole o più righe.
    # Con l'archivio annuale disponibile usiamo direttamente le proclamazioni:
    # nessuna deduplicazione basata solo su data/luogo/sigla (perderebbe scioperi).
    manuali = [e for e in base["eventi"] if not (
        official and e["type"] == "sciopero" and "mit" in e.get("src", []))]
    eventi = sorted(manuali + official, key=lambda e: (e["start"], e["id"]))
    if len({e["id"] for e in eventi}) != len(eventi):
        raise ValueError("ID duplicati nell'archivio unito")
    return {
        "base": base, "luoghi": {**mit.get("luoghi", {}), **base["luoghi"]},
        "eventi": eventi, "aggiornato": max(base["snapshot"], mit.get("aggiornato", "")),
        "n_auto": len(official), "doppi": [], "da_verificare": [],
        "archive": {
            "year": 2026, "from": "2026-01-01", "to": "2026-12-31",
            "syncedAt": mit.get("sincronizzato", ""), "sourceRows": mit.get("righe_lette", 0),
            "officialCount": len(official), "manualCount": len(manuali),
            "revokedCount": sum(e.get("official_status") == "revocato" for e in official),
            "missingCount": sum(bool(e.get("not_in_latest")) for e in official),
        },
    }
