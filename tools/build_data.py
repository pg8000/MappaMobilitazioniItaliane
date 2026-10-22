"""Unisce gli eventi manuali (data/eventi.json) e quelli automatici (data/scioperi-mit.json)."""
from comuni import carica, DATA


def stesso_sciopero(m, e):
    """m = evento MIT, e = evento manuale: stesso sciopero?"""
    if m["start"] != e["start"] or e["type"] != "sciopero":
        return False
    if m.get("place") != e.get("place"):
        return False
    return bool(set(m["orgs"]) & set(e["orgs"])) or (m.get("place") and m["sector"] == e["sector"])


def unisci():
    base = carica("eventi.json")
    mit = carica("scioperi-mit.json") if (DATA / "scioperi-mit.json").exists() else {"eventi": [], "luoghi": {}}
    manuali = base["eventi"]
    doppi, aggiunti = [], []
    for m in mit["eventi"]:
        if any(stesso_sciopero(m, e) for e in manuali):
            doppi.append(m["id"])
        else:
            aggiunti.append(m)
    # scioperi manuali che citano il MIT, futuri, ma non più presenti nel calendario: possibile revoca
    da_verificare = []
    if mit["eventi"]:
        for e in manuali:
            if e["type"] == "sciopero" and "mit" in e.get("src", []) and e["end"] >= mit.get("aggiornato", "") \
                    and not any(stesso_sciopero(m, e) for m in mit["eventi"]):
                da_verificare.append(e["id"])
    luoghi = dict(base["luoghi"])
    for k, v in mit["luoghi"].items():
        if any(a.get("place") == k for a in aggiunti):
            luoghi.setdefault(k, v)
    return {
        "base": base, "luoghi": luoghi, "eventi": manuali + aggiunti,
        "aggiornato": max(base["snapshot"], mit.get("aggiornato", "")),
        "doppi": doppi, "da_verificare": da_verificare, "n_auto": len(aggiunti),
    }
