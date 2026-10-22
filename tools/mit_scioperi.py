#!/usr/bin/env python3
"""Scarica il calendario scioperi del Ministero dei Trasporti e scrive data/scioperi-mit.json.

Uso: python tools/mit_scioperi.py [file.html]   (con un file usa quello invece di scaricare: serve per i test)
Non sovrascrive nulla se la tabella non viene riconosciuta o non contiene righe.
"""
import hashlib, re, sys, urllib.request, urllib.parse, datetime as dt, time
from html.parser import HTMLParser
from comuni import carica, salva, oggi, senza_accenti, slug, province

URL = "https://scioperi.mit.gov.it/mit2/public/scioperi/ricerca"
YEAR = 2026
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
            low = [senza_accenti(c).lower().strip().rstrip("*") for c in riga]
            low = ["modalita" if c.startswith("modalit") else c for c in low]
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
    "trasporto aereo": "Trasporto aereo", "aereo": "Trasporto aereo", "ferroviario": "Treni",
    "trasporto marittimo": "Porti", "marittimo": "Porti", "porti": "Porti",
    "trasporto merci": "Trasporto merci", "appalti ferroviari": "Appalti ferroviari",
    "generale": "Generale", "plurisettoriale": "Plurisettoriale",
    "circolazione e sicurezza stradale": "Autostrade", "autostrade": "Autostrade",
}
RILEVANZA = {"locale": "locale", "regionale": "regionale", "nazionale": "nazionale",
             "interregionale": "multiregionale", "multiregionale": "multiregionale",
             "provinciale": "locale", "territoriale": "locale", "aziendale": "locale", "da definire": "multiregionale"}
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
        if fin < da or ini > a:
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
        if not area and regione and regione.lower() != "italia":
            area = f"Regione {regione}"
        sett = r.get("settore", "").strip()
        modalita = r.get("modalità") or r.get("modalita") or ""
        ev = {
            "id": "mit-" + hashlib.sha1("|".join([r["inizio"], r.get("fine", ""), sind, r.get("categoria", ""), regione, provincia, r.get("data proclamazione", ""), r.get("data ricezione", "")]).encode()).hexdigest()[:16],
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
            ev["note"] = r["note"]
        ev["src"] = ["mit"]
        stato = r.get("stato", "").lower()
        ev["official_status"] = "revocato" if "revocat" in stato else "effettuato" if "effettuat" in stato else "in programma"
        ev["source_category"] = r.get("categoria", "")
        ev["source_union"] = sind
        ev["source_region"] = regione
        ev["source_province"] = provincia
        ev["proclaimed_at"] = r.get("data proclamazione", "")
        ev["received_at"] = r.get("data ricezione", "")
        ev["verified_at"] = oggi_.isoformat()
        eventi.append(ev)
    return eventi, luoghi, scartati


def scarica_anno():
    # Il prospetto iniziale contiene soltanto gli eventi recenti. Il form storico
    # restituisce invece tutto l'anno e lo stato (compresi i revocati).
    body = urllib.parse.urlencode({
        "dataInizio": f"01/01/{YEAR}", "dataFine": f"31/12/{YEAR}",
        "categoria": "", "sindacato": "", "settore": "0", "rilevanza": "0",
        "stato": "0", "submit": "Ricerca",
    }).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, data=body, headers={"User-Agent": UA, "Accept-Language": "it"})
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read().decode("utf-8", "replace")
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def main():
    base, prov = carica("eventi.json"), province()
    html = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else scarica_anno()
    righe = leggi_righe(html)
    if not righe or not all({"inizio", "fine", "sindacati", "categoria", "stato"} <= r.keys() for r in righe):
        sys.exit("ERRORE: archivio MIT non riconosciuto. Ultimo archivio valido conservato.")
    eventi, luoghi, scartati = converti(righe, base, prov, oggi())
    if scartati or not eventi:
        sys.exit(f"ERRORE: {scartati} date non leggibili o archivio vuoto. Dati precedenti conservati.")
    by_id = {}
    for e in eventi:
        old = by_id.get(e["id"])
        if not old or (e["official_status"] == "revocato" and old["official_status"] != "revocato"):
            by_id[e["id"]] = e
    # Una voce assente non equivale a una revoca: rimane archiviata e viene
    # segnalata come non riscontrata nell'ultima verifica.
    precedente = carica("scioperi-mit.json")
    for e in precedente.get("eventi", []):
        if e["id"] not in by_id and e["start"][:4] == str(YEAR):
            by_id[e["id"]] = dict(e, not_in_latest=True)
    luoghi = {**precedente.get("luoghi", {}), **luoghi}
    result = list(by_id.values())
    print(f"MIT {YEAR}: {len(righe)} righe, {len(result)} voci archiviate, "
          f"{sum(e['official_status'] == 'revocato' for e in result)} revocate")
    salva("scioperi-mit.json", {
        "fonte": URL, "anno": YEAR, "aggiornato": oggi().isoformat(),
        "sincronizzato": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "righe_lette": len(righe), "copertura": {"da": f"{YEAR}-01-01", "a": f"{YEAR}-12-31"},
        "luoghi": luoghi, "eventi": sorted(result, key=lambda e: (e["start"], e["id"])),
    })


if __name__ == "__main__":
    main()
