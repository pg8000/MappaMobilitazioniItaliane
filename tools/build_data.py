"""Archivio unico: proclamazioni MIT autorevoli e iniziative curate a mano."""
from comuni import carica, DATA, province, posizione_regionale


def unisci():
    base = carica("eventi.json")
    verified = carica("eventi-verificati.json") if (DATA / "eventi-verificati.json").exists() else {"fonti": {}, "eventi": []}
    if verified.get("versione", 1) != 1:
        raise ValueError("Formato eventi verificati non riconosciuto")
    base = dict(base, fonti={**base["fonti"], **verified["fonti"]})
    mit = carica("scioperi-mit.json") if (DATA / "scioperi-mit.json").exists() else {}
    official = mit.get("eventi", [])
    # Le vecchie schede manuali MIT erano un riassunto di singole o più righe.
    # Con l'archivio annuale disponibile usiamo direttamente le proclamazioni:
    # nessuna deduplicazione basata solo su data/luogo/sigla (perderebbe scioperi).
    manuali = [e for e in base["eventi"] if not (
        official and e["type"] == "sciopero" and "mit" in e.get("src", []))]
    prov = province()
    luoghi = {**prov, **mit.get("luoghi", {}), **base["luoghi"]}
    from valida import errori_evento
    for event in verified["eventi"]:
        if not str(event.get("id", "")).startswith("ver-") or event.get("type") != "manifestazione":
            raise ValueError("Evento verificato non valido")
        errors = errori_evento(event, base, luoghi)
        if errors:
            raise ValueError("Evento verificato non valido: " + "; ".join(errors))
    eventi = sorted((posizione_regionale(e, luoghi, prov) for e in manuali + official + verified["eventi"]), key=lambda e: (e["start"], e["id"]))
    if len({e["id"] for e in eventi}) != len(eventi):
        raise ValueError("ID duplicati nell'archivio unito")
    return {
        "base": base, "luoghi": luoghi,
        "eventi": eventi, "aggiornato": max(base["snapshot"], mit.get("aggiornato", "")),
        "n_auto": len(official), "doppi": [], "da_verificare": [],
        "archive": {
            "year": 2026, "from": "2026-01-01", "to": "2026-12-31",
            "syncedAt": mit.get("sincronizzato", ""), "sourceRows": mit.get("righe_lette", 0),
            "officialCount": len(official), "manualCount": len(manuali),
            "verifiedCount": len(verified["eventi"]),
            "revokedCount": sum(e.get("official_status") == "revocato" for e in official),
            "missingCount": sum(bool(e.get("not_in_latest")) for e in official),
        },
    }
