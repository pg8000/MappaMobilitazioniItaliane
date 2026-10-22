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
