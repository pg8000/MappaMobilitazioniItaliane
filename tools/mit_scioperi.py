#!/usr/bin/env python3
"""Scarica il calendario scioperi del Ministero dei Trasporti e scrive data/scioperi-mit.json.

Uso: python tools/mit_scioperi.py [file.html]   (con un file usa quello invece di scaricare: serve per i test)
Non sovrascrive nulla se la tabella non viene riconosciuta o non contiene righe.
"""
import hashlib, re, sys, urllib.request, urllib.parse, urllib.error, datetime as dt, time
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from comuni import carica, salva, oggi, senza_accenti, slug, province, posizione_regionale

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
        if r.get("mit_guid"):
            ev["mit_guid"] = normalizza_guid(r["mit_guid"])
        eventi.append(posizione_regionale(ev, luoghi, prov))
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
    try:
        html = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else scarica_anno()
    except urllib.error.HTTPError as exc:
        if exc.code < 500:
            raise
        print(f"MIT temporaneamente non disponibile: HTTP {exc.code}", file=sys.stderr)
        sys.exit(75)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"MIT temporaneamente non disponibile: {exc}", file=sys.stderr)
        sys.exit(75)
    righe = leggi_righe(html)
    if not righe or not all({"inizio", "fine", "sindacati", "categoria", "stato"} <= r.keys() for r in righe):
        sys.exit("ERRORE: archivio MIT non riconosciuto. Ultimo archivio valido conservato.")
    eventi, luoghi, scartati = converti(righe, base, prov, oggi())
    if scartati or not eventi:
        sys.exit(f"ERRORE: {scartati} date non leggibili o archivio vuoto. Dati precedenti conservati.")
    precedente = carica("scioperi-mit.json")
    eventi = riconcilia_annuale(eventi, precedente.get("eventi", []))
    by_id = {}
    for e in eventi:
        old = by_id.get(e["id"])
        if not old or (e["official_status"] == "revocato" and old["official_status"] != "revocato"):
            by_id[e["id"]] = e
    # Una voce assente non equivale a una revoca: rimane archiviata e viene
    # segnalata come non riscontrata nell'ultima verifica.
    for e in precedente.get("eventi", []):
        if e["id"] not in by_id and e["start"][:4] == str(YEAR):
            by_id[e["id"]] = dict(e, not_in_latest=True)
    luoghi = {**precedente.get("luoghi", {}), **luoghi}
    result = list(by_id.values())
    print(f"MIT {YEAR}: {len(righe)} righe, {len(result)} voci archiviate, "
          f"{sum(e['official_status'] == 'revocato' for e in result)} revocate")
    salva("scioperi-mit.json", {
        **{k: v for k, v in precedente.items() if k.startswith("rss_")},
        "fonte": URL, "anno": YEAR, "aggiornato": oggi().isoformat(),
        "sincronizzato": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "righe_lette": len(righe), "copertura": {"da": f"{YEAR}-01-01", "a": f"{YEAR}-12-31"},
        "luoghi": luoghi, "eventi": sorted(result, key=lambda e: (e["start"], e["id"])),
    })




# Feed ufficiale dei prossimi scioperi: fonte integrativa, mai sostitutiva dello storico.
RSS_URL = "https://scioperi.mit.gov.it/mit2/public/scioperi/rss"


def leggi_rss(xml):
    from html import unescape
    if len(xml) > 2_000_000 or re.search(r"<!DOCTYPE|<!ENTITY", xml, re.I):
        raise ValueError("Feed MIT RSS eccessivo o con dichiarazioni non consentite")
    root = ET.fromstring(xml)
    if root.tag != "rss":
        raise ValueError("Feed MIT RSS non riconosciuto")
    righe, guids = [], set()
    for item in root.findall("./channel/item"):
        title = item.findtext("title", "")
        desc = unescape(item.findtext("description", "") or "")
        campi = {}
        for parte in re.split(r"<br\s*/?>", desc, flags=re.I):
            if ":" in parte:
                k, v = parte.split(":", 1)
                campi[k.strip().lower()] = v.strip()
        def titolo_campo(nome):
            m = re.search(r"(?:^| - )" + re.escape(nome) + r":\s*(.*?)(?= - [^:]+:|$)", title)
            return m.group(1).strip() if m else ""
        r = {
            "inizio": titolo_campo("Data inizio"),
            "fine": campi.get("data fine", ""),
            "settore": campi.get("settore") or titolo_campo("Settore"),
            "rilevanza": campi.get("rilevanza") or titolo_campo("Rilevanza"),
            "regione": campi.get("regione") or titolo_campo("Regione"),
            "provincia": campi.get("provincia") or titolo_campo("Provincia"),
            "sindacati": campi.get("sindacati", ""),
            "categoria": campi.get("categoria interessata", ""),
            "modalità": campi.get("modalità", ""),
            "data proclamazione": campi.get("data proclamazione", ""),
            "data ricezione": campi.get("data ricezione", ""),
        }
        if not r["inizio"] or not r["fine"] or not r["categoria"]:
            raise ValueError("Elemento RSS MIT incompleto")
        r["mit_guid"] = normalizza_guid(item.findtext("guid", ""))
        if r["mit_guid"] in guids:
            raise ValueError("GUID RSS MIT duplicato")
        guids.add(r["mit_guid"])
        if data_it(r["fine"]) < data_it(r["inizio"]):
            raise ValueError("Intervallo RSS MIT non valido")
        righe.append(r)
    if not righe:
        raise ValueError("Feed MIT RSS vuoto")
    return righe


def scarica_rss():
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml"})
    with urllib.request.urlopen(req, timeout=25) as response:
        content = response.read(2_000_001)
        if len(content) > 2_000_000:
            raise ValueError("Feed MIT RSS eccessivo")
        return content.decode("utf-8-sig")


def normalizza_guid(value):
    """Identificativo MIT stabile, indipendente da schema HTTP/HTTPS."""
    value = str(value).strip()
    if value.isdecimal():
        return value
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme in ("http", "https") and parsed.netloc == "scioperi.mit.gov.it"
            and re.fullmatch(r"/[0-9]+/?", parsed.path) and not parsed.query and not parsed.fragment):
        return parsed.path.strip("/")
    raise ValueError("GUID RSS MIT assente o non valido")


def chiave_evento(event):
    """Ponte conservativo verso lo storico privo di GUID.

    L'RSS omette l'ora di ricezione presente nella tabella; confrontiamo il giorno,
    ma non fondiamo mai più candidati indistinguibili con questa precisione.
    """
    fields = ("start", "end", "sector", "source_union", "source_category",
              "source_region", "source_province", "proclaimed_at", "received_at")
    return tuple(" ".join(senza_accenti(str(event.get(k, ""))[:10] if k.endswith("_at")
                                       else str(event.get(k, ""))).lower().split()) for k in fields)


def trova_evento(event, events):
    guid = event.get("mit_guid")
    if guid:
        matches = [e for e in events if e.get("mit_guid") and normalizza_guid(e["mit_guid"]) == guid]
        if matches:
            return matches[0] if len(matches) == 1 else False
    exact = [e for e in events if e["id"] == event["id"]]
    if exact:
        return exact[0]
    matches = [e for e in events if chiave_evento(e) == chiave_evento(event)
               and (not guid or not e.get("mit_guid") or normalizza_guid(e["mit_guid"]) == guid)]
    return matches[0] if len(matches) == 1 else False if matches else None


def riconcilia_annuale(events, previous):
    result = []
    for event in events:
        # Solo il GUID o l'identità completa e univoca possono collegare le fonti.
        old = trova_evento(event, previous)
        if old and old["id"] != event["id"] and sum(chiave_evento(e) == chiave_evento(event) for e in events) != 1:
            old = None
        if old:
            event = dict(event, id=old["id"])
            for key in ("mit_guid", "rss_seen_at"):
                if old.get(key):
                    event[key] = old[key]
        result.append(event)
    return result


def fondi_rss(previous, events, places, item_count, checked_at):
    by_id = {e["id"]: dict(e) for e in previous.get("eventi", [])}
    added = ambiguous = 0
    for event in events:
        old = trova_evento(event, list(by_id.values()))
        if old is False:
            ambiguous += 1
            continue
        if old:
            # La tabella annuale resta autorevole per contenuti e stati ufficiali.
            if old.get("source_feed") == "rss":
                by_id[old["id"]] = dict(event, id=old["id"], source_feed="rss",
                                        official_status=old["official_status"])
            by_id[old["id"]].update(mit_guid=event["mit_guid"], rss_seen_at=checked_at)
        else:
            event = dict(event, id="mit-rss-" + event["mit_guid"], source_feed="rss", rss_seen_at=checked_at)
            by_id[event["id"]] = event
            added += 1
    return dict(previous, eventi=sorted(by_id.values(), key=lambda e: (e["start"], e["id"])),
                luoghi={**previous.get("luoghi", {}), **places}, rss_checked_at=checked_at,
                rss_items=item_count, rss_added=added, rss_ambiguous=ambiguous)


def integra_rss():
    # L'RSS non pubblica stati ufficiali: non modificare mai revoche o conferme esistenti.
    try:
        righe = leggi_rss(scarica_rss())
    except (OSError, TimeoutError, ValueError, ET.ParseError) as exc:
        print(f"MIT RSS non disponibile: {exc}; archivio invariato", file=sys.stderr)
        if __import__("os").environ.get("GITHUB_ACTIONS"):
            print("::warning::Feed RSS MIT non disponibile: archivio precedente conservato")
        return False
    base, prov = carica("eventi.json"), province()
    nuovi, luoghi, scartati = converti(righe, base, prov, oggi())
    if scartati:
        print("MIT RSS: dati incompleti; archivio invariato", file=sys.stderr)
        return False
    precedente = carica("scioperi-mit.json")
    risultato = fondi_rss(precedente, nuovi, luoghi, len(righe),
                          dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    salva("scioperi-mit.json", risultato)
    print(f"MIT RSS: {len(righe)} voci lette, {risultato['rss_added']} nuovi eventi integrati, "
          f"{risultato['rss_ambiguous']} corrispondenze ambigue non importate")
    if risultato['rss_ambiguous']:
        print("::warning::RSS MIT: corrispondenze ambigue conservate senza fusione né nuovi duplicati")
    return True

if __name__ == "__main__":
    if sys.argv[1:] == ["--rss"]:
        integra_rss()
    else:
        main()


