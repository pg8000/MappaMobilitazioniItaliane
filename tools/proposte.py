#!/usr/bin/env python3
"""Cerca nelle notizie (Google News RSS) manifestazioni annunciate e le propone come issue GitHub con etichetta `proposta`.
Niente viene pubblicato sulla mappa finché non lo approvi tu con l'etichetta `approva`.
Senza GITHUB_TOKEN stampa soltanto le proposte (prova a secco). Uso: python tools/proposte.py"""
import hashlib, json, os, re, sys, urllib.parse, urllib.request, datetime as dt, email.utils
import xml.etree.ElementTree as ET
from comuni import carica, salva, oggi, slug, province, DATA

UA = "MappaMobilitazioniItaliane/2 (+https://github.com/pg8000/MappaMobilitazioniItaliane)"
QUERY = ['corteo OR manifestazione OR presidio OR "sit-in" OR fiaccolata when:3d',
         'manifestazione nazionale OR "corteo nazionale" when:7d']
PAROLE = re.compile(r"\b(corteo|cortei|manifestazion\w*|presidio|presidi|sit-in|fiaccolata|mobilitazion\w*)\b", re.I)
ESCLUDI = re.compile(r"\b(sciopero|scioperi|calcio|partita|concerto|gp |gara)\b", re.I)
MESI = {m: i + 1 for i, m in enumerate("gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split())}
GIORNI = {"lunedì": 0, "martedì": 1, "mercoledì": 2, "giovedì": 3, "venerdì": 4, "sabato": 5, "domenica": 6}
MAX_PER_RUN = 8


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=40).read()


def data_probabile(testo, pub):
    m = re.search(r"\b(\d{1,2})\s+(" + "|".join(MESI) + r")\b", testo, re.I)
    if m:
        g, mese = int(m.group(1)), MESI[m.group(2).lower()]
        for anno in (pub.year, pub.year + 1):
            try:
                d = dt.date(anno, mese, g)
            except ValueError:
                continue
            if d >= pub - dt.timedelta(days=1):
                return d
    low = testo.lower()
    if "domani" in low:
        return pub + dt.timedelta(days=1)
    for nome, n in GIORNI.items():
        if re.search(r"\b" + nome + r"\b", low):
            return pub + dt.timedelta(days=(n - pub.weekday()) % 7 or 7)
    return None


def candidati(prov):
    nomi = sorted(((v["name"], k) for k, v in prov.items()), key=lambda x: -len(x[0]))
    visti = set()
    for q in QUERY:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, "hl": "it", "gl": "IT", "ceid": "IT:it"})
        try:
            root = ET.fromstring(scarica(url))
        except Exception as e:
            print("feed non leggibile:", e, file=sys.stderr)
            continue
        for it in root.iter("item"):
            titolo, link = (it.findtext("title") or "").strip(), (it.findtext("link") or "").strip()
            if not titolo or not link.startswith("https://") or link in visti:
                continue
            visti.add(link)
            if not PAROLE.search(titolo) or ESCLUDI.search(titolo):
                continue
            pub = email.utils.parsedate_to_datetime(it.findtext("pubDate")).date() if it.findtext("pubDate") else oggi()
            if (oggi() - pub).days > 5:
                continue
            testata = (it.findtext("source") or "").strip()
            titolo_pulito = re.sub(r"\s+-\s+" + re.escape(testata) + r"$", "", titolo) if testata else titolo
            luogo = next((k for n, k in nomi if re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", titolo_pulito, re.I)), None)
            if not luogo:
                continue
            yield {"titolo": titolo_pulito, "link": link, "testata": testata or "Google News", "pub": pub,
                   "luogo": luogo, "data": data_probabile(titolo_pulito, pub)}


def corpo(c, prov):
    bozza = {
        "id": "", "type": "manifestazione", "scope": "locale", "sector": "DA COMPILARE",
        "place": c["luogo"], "start": c["data"].isoformat() if c["data"] else "DA COMPILARE",
        "end": c["data"].isoformat() if c["data"] else "DA COMPILARE",
        "time": "", "title": c["titolo"], "who": "DA COMPILARE", "where": "",
        "orgs": ["non-identificato"],
        "fonte": {"nome": f"{c['testata']}, {c['pub'].strftime('%d/%m/%Y')}", "url": c["link"]},
    }
    return (
        f"**Proposta automatica: da verificare prima di approvarla.**\n\n"
        f"Notizia: [{c['titolo']}]({c['link']}) ({c['testata']}, {c['pub'].strftime('%d/%m/%Y')}).\n\n"
        "Per pubblicarla sulla mappa:\n\n"
        "1. Apri la fonte e controlla data, luogo e organizzatore. Se manca uno dei tre, chiudi la issue.\n"
        "2. Correggi il blocco JSON qui sotto (modifica questa issue): titolo neutro e breve, `sector`, `who`, `orgs` (chiavi in `data/eventi.json`), orario. "
        "Niente nomi di persone, niente numeri di partecipanti.\n"
        "3. Aggiungi l'etichetta `approva`. Per scartarla, chiudi la issue.\n\n"
        "Le manifestazioni non preavvisate, vietate o con scontri sono *eventi eccezionali*: non si approvano da qui ma si inseriscono a mano.\n\n"
        f"```json\n{json.dumps(bozza, ensure_ascii=False, indent=2)}\n```\n"
    )


def apri_issue(repo, token, titolo, body):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues",
        data=json.dumps({"title": titolo, "body": body, "labels": ["proposta"]}).encode(),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": UA},
    )
    return json.load(urllib.request.urlopen(req, timeout=40))["html_url"]


def main():
    prov = province()
    viste_f = DATA / "proposte-viste.json"
    viste = set(json.loads(viste_f.read_text(encoding="utf-8"))) if viste_f.exists() else set()
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    n = 0
    for c in candidati(prov):
        chiavi = {"u:" + hashlib.sha1(c["link"].encode()).hexdigest()[:12]}
        if c["data"]:
            chiavi.add(f"{c['luogo']}:{c['data'].isoformat()}")
        if chiavi & viste:
            continue
        if n >= MAX_PER_RUN:
            break
        titolo = f"Proposta: {c['titolo'][:90]}"
        if repo and token:
            print("aperta", apri_issue(repo, token, titolo, corpo(c, prov)))
        else:
            print("[prova a secco]", titolo, "|", c["luogo"], c["data"])
        viste |= chiavi
        n += 1
    if repo and token:
        viste_f.write_text(json.dumps(sorted(viste), indent=1) + "\n", encoding="utf-8")
    print(f"{n} proposte")


if __name__ == "__main__":
    main()
