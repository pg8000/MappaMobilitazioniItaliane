#!/usr/bin/env python3
"""Scarica il calendario scioperi del Ministero dei Trasporti e scrive data/scioperi-mit.json.

Uso: python tools/mit_scioperi.py [file.html]   (con un file usa quello invece di scaricare: serve per i test)
Non sovrascrive nulla se la tabella non viene riconosciuta o non contiene righe.
"""
import hashlib, re, sys, urllib.request, datetime as dt
from html.parser import HTMLParser
from comuni import carica, salva, oggi, senza_accenti, slug, province

URL = "https://scioperi.mit.gov.it/mit2/public/scioperi"
UA = "MappaMobilitazioniItaliane/2 (+https://github.com/pg8000/MappaMobilitazioniItaliane)"


class TabelleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tabelle, self._t, self._r, self._c = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._t = []
        elif tag == "tr" and self._t is not None:
            self._r = []
        elif tag in ("td", "th") and self._r is not None:
            self._c = []
        elif tag == "br" and self._c is not None:
            self._c.append(" ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._c is not None and self._r is not None:
            self._r.append(" ".join("".join(self._c).split()))
            self._c = None
        elif tag == "tr" and self._r is not None and self._t is not None:
            if self._r:
                self._t.append(self._r)
            self._r = None
        elif tag == "table" and self._t is not None:
            self.tabelle.append(self._t)
            self._t = None

    def handle_data(self, d):
        if self._c is not None:
            self._c.append(d)


def leggi_righe(html):
    p = TabelleHTML()
    p.feed(html)
    for tab in p.tabelle:
        for i, riga in enumerate(tab):
            low = [c.lower() for c in riga]
            if "inizio" in low and any(c.startswith("sindacat") for c in low):
                intest = low
                righe = []
                for r in tab[i + 1:]:
                    if len(r) < len(intest):
                        continue
                    r = r[len(r) - len(intest):]
                    righe.append({intest[k]: r[k] for k in range(len(intest)) if intest[k]})
                return righe
    return []


# ---- normalizzazione -------------------------------------------------------------------
ALIAS = [  # dal più specifico al più generico
    (r"FILT[-\s]?CGIL", "filt-cgil"), (r"FP[-\s]?CGIL", "fp-cgil"), (r"FILCAMS(?:[-\s]?CGIL)?", "filcams-cgil"),
    (r"FIT[-\s]?CISL", "fit-cisl"), (r"FISASCAT(?:[-\s]?CISL)?", "fisascat-cisl"),
    (r"UILTUCS", "uiltucs"), (r"UILTRASPORTI|UILT(?:[-\s]?UIL)?", "uiltrasporti"),
    (r"FAISA(?:[-\s]?CISAL)?", "faisa-cisal"), (r"ORSA(?:\s+FERROVIE)?", "orsa-ferrovie"),
    (r"FAST[-\s]?CONFSAL", "fast-confsal"), (r"FAST[-\s]?MOBILITA'?", "fast-mobilita"),
    (r"USI[-\s]?CIT", "usi-cit"), (r"ADL[-\s]?COBAS", "adl-cobas"), (r"SIAL[-\s]?COBAS", "sial-cobas"),
    (r"AL[-\s]?COBAS", "al-cobas"), (r"CIB[-\s]?UNICOBAS|UNICOBAS", "cib-unicobas"), (r"COBAS", "cobas"),
    (r"CLAP", "clap"), (r"USB", "usb"), (r"CUB", "cub"), (r"SGB", "sgb"), (r"UGL", "ugl"), (r"CGIL", "cgil"),
]
SETTORI = {
    "trasporto pubblico locale": "Trasporto locale", "trasporto ferroviario": "Treni", "ferrovie": "Treni",
    "trasporto aereo": "Trasporto aereo", "trasporto marittimo": "Porti", "porti": "Porti",
    "circolazione e sicurezza stradale": "Autostrade", "autostrade": "Autostrade",
}
RILEVANZA = {"locale": "locale", "regionale": "regionale", "nazionale": "nazionale",
             "interregionale": "multiregionale", "multiregionale": "multiregionale"}
PICCOLE = {"di", "del", "della", "dei", "delle", "e", "ed", "a", "in", "per", "da", "al", "alla", "il", "la", "le", "i", "lo"}


def sigle(testo, promotori):
    t = " " + senza_accenti(testo).upper().replace("–", "-").replace("—", "-") + " "
    trovate = []
    for pat, chiave in ALIAS:
        rx = re.compile(r"(?<![A-Z0-9])(?:" + pat + r")(?![A-Z0-9])")
        if rx.search(t):
            if chiave not in trovate and chiave in promotori:
                trovate.append(chiave)
            t = rx.sub(" ", t)
    return trovate


def titolo(s):
    parole = s.lower().split()
    out = [w if (i and w in PICCOLE) else (w[:1].upper() + w[1:]) for i, w in enumerate(parole)]
    return " ".join(out)[:140]


def data_it(s):
    return dt.datetime.strptime(s.strip()[:10], "%d/%m/%Y").date()


def converti(righe, base, prov, oggi_):
    per = base["periodo"]["scioperi_e_manifestazioni"]
    da, a = dt.date.fromisoformat(per["da"]), dt.date.fromisoformat(per["a"])
    prom = base["promotori"]
    eventi, luoghi, scartati = [], {}, 0
    for r in righe:
        try:
            ini, fin = data_it(r["inizio"]), data_it(r.get("fine") or r["inizio"])
        except (KeyError, ValueError):
            scartati += 1
            continue
        if fin < max(da, oggi_) or ini > a:
            continue
        sind = r.get("sindacati", "")
        orgs = sigle(sind, prom) or ["non-identificato"]
        rilev = RILEVANZA.get(r.get("rilevanza", "").strip().lower(), "locale")
        regione, provincia = r.get("regione", "").strip(), r.get("provincia", "").strip()
        place, area = None, None
        chiave = slug(provincia)
        if rilev in ("locale", "regionale") and chiave in prov and regione.lower() != "italia":
            place = chiave
            luoghi[place] = prov[place]
            if rilev == "regionale":
                area = f"Regione {regione}; punto su {prov[place]['name']}"
        elif rilev != "nazionale":
            area = ", ".join(x for x in (regione, provincia) if x and x.lower() not in ("italia", "tutte")) or None
        sett = r.get("settore", "").strip()
        modalita = r.get("modalità") or r.get("modalita") or ""
        ev = {
            "id": "mit-" + hashlib.sha1("|".join([r["inizio"], r.get("fine", ""), sind, r.get("categoria", ""), regione, provincia]).encode()).hexdigest()[:10],
            "orgs": orgs, "type": "sciopero", "scope": rilev,
            "sector": SETTORI.get(sett.lower(), sett or "Altro"),
        }
        if place:
            ev["place"] = place
        ev.update({
            "start": ini.isoformat(), "end": fin.isoformat(),
            "time": (modalita[:1].upper() + modalita[1:].lower()) if modalita else "intera giornata",
            "title": titolo(r.get("categoria", "")) or "Sciopero",
            "who": ", ".join(prom[o]["nome"] for o in orgs) if orgs != ["non-identificato"] else sind[:120],
        })
        if area:
            ev["area"] = area
        if r.get("note"):
            ev["note"] = r["note"][:200]
        ev["src"] = ["mit"]
        eventi.append(ev)
    return eventi, luoghi, scartati


def main():
    base, prov = carica("eventi.json"), province()
    if len(sys.argv) > 1:
        html = open(sys.argv[1], encoding="utf-8").read()
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept-Language": "it"})
        html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    righe = leggi_righe(html)
    if not righe:
        sys.exit("ERRORE: nessuna riga riconosciuta nella tabella MIT (la pagina è cambiata?). Dati non modificati.")
    eventi, luoghi, scartati = converti(righe, base, prov, oggi())
    print(f"MIT: {len(righe)} righe lette, {len(eventi)} nel periodo, {scartati} con data non leggibile")
    salva("scioperi-mit.json", {
        "fonte": URL, "aggiornato": oggi().isoformat(), "righe_lette": len(righe),
        "luoghi": luoghi, "eventi": sorted(eventi, key=lambda e: (e["start"], e["id"])),
    })


if __name__ == "__main__":
    main()
