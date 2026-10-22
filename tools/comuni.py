"""Funzioni condivise: lettura/scrittura JSON, date, slug, tabella delle province."""
import json, re, unicodedata, datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def carica(nome):
    return json.loads((DATA / nome).read_text(encoding="utf-8"))


def salva(nome, obj):
    (DATA / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def oggi():
    return dt.datetime.now(ZoneInfo("Europe/Rome")).date()


def senza_accenti(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def slug(s):
    s = senza_accenti(s).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def province():
    """slug -> {name, lon, lat}"""
    out = {}
    for nome, c in carica("province.json")["province"].items():
        out[slug(nome)] = {"name": nome, "lon": c["lon"], "lat": c["lat"]}
    return out


# Coordinate già presenti nella tabella delle province: il punto è soltanto
# un indicatore dell'area regionale, non il luogo fisico dello sciopero.
REGIONI = {
    "Abruzzo": "L'Aquila", "Basilicata": "Potenza", "Calabria": "Catanzaro",
    "Campania": "Napoli", "Emilia-Romagna": "Bologna", "Friuli-Venezia Giulia": "Trieste",
    "Lazio": "Roma", "Liguria": "Genova", "Lombardia": "Milano", "Marche": "Ancona",
    "Molise": "Campobasso", "Piemonte": "Torino", "Puglia": "Bari", "Sardegna": "Cagliari",
    "Sicilia": "Palermo", "Toscana": "Firenze", "Trentino-Alto Adige": "Trento",
    "Umbria": "Perugia", "Valle d'Aosta": "Aosta", "Veneto": "Venezia",
}


def posizione_regionale(evento, luoghi, prov):
    """Dà un indicatore alle voci regionali senza una provincia, senza mutare gli input."""
    if evento.get("place") or evento.get("scope") != "regionale":
        return evento
    raw = evento.get("source_region") or evento.get("area", "")
    key = slug(raw.removeprefix("Regione ")).replace("-", "")
    for regione, capoluogo in REGIONI.items():
        if key != slug(regione).replace("-", ""):
            continue
        cap = prov.get(slug(capoluogo))
        if not cap:
            return evento
        place = "regione-" + slug(regione)
        luoghi[place] = {**cap, "name": f"{regione} (regione)", "kind": "region",
                         "region": regione, "anchor": capoluogo}
        area = f"{evento.get('area') or regione}; indicatore regionale presso {capoluogo}, non luogo puntuale"
        return dict(evento, place=place, area=area, map_precision="region")
    return evento
