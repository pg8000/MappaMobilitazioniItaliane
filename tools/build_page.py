"""Genera index.html dal sorgente (tools/sorgente-artifact.html) e dai dati in data/.
Uso: python tools/build_page.py [REPO_URL]
- sostituisce SRC, PLACES, ORGS ed EVENTS con i dati uniti (manuali + calendario MIT)
- toglie Google Fonts (privacy dei visitatori) e usa font di sistema
- aggiunge scheletro HTML, Content-Security-Policy e Referrer-Policy
- aggiunge il piè di pagina con link al repository e alle segnalazioni"""
import sys, re, json, datetime as dt
from comuni import ROOT
from build_data import unisci

REPO = (sys.argv[1] if len(sys.argv) > 1 else "https://github.com/pg8000/MappaMobilitazioniItaliane").rstrip("/")
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


d = unisci()
base = d["base"]
s = (ROOT / "tools" / "sorgente-artifact.html").read_text(encoding="utf-8")

# ---- dati ---------------------------------------------------------------------------
i0, i1 = s.index("const SRC = {"), s.index("\n];", s.index("const EVENTS = [")) + 3
famiglie = re.search(r"const FAMILIES=\[.*?\];", s, re.S).group(0)
nuovo = "\n".join([
    "const SRC = " + js({k: [v["nome"], v["url"]] for k, v in base["fonti"].items()}) + ";",
    "const PLACES = " + js(d["luoghi"]) + ";",
    "const ORGS = " + js({k: [v["nome"], v["famiglia"]] for k, v in base["promotori"].items()}) + ";",
    famiglie,
    "const EVENTS = " + js(d["eventi"]) + ";",
])
s = s[:i0] + nuovo + s[i1:]
agg = dt.date.fromisoformat(d["aggiornato"])
s, n = re.subn(r"(Dati aggiornati al <b>)[^<]*(</b>)", rf"\g<1>{agg.day} {MESI[agg.month - 1]} {agg.year}\g<2>", s)
assert n == 1

# ---- pagina pubblica -----------------------------------------------------------------
s = re.sub(r'<link rel="preconnect"[^>]*>\n', '', s)
s = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', '', s)
s = s.replace('--f-display:"IBM Plex Sans Condensed","Arial Narrow",system-ui,sans-serif;',
              '--f-display:"Avenir Next Condensed","Roboto Condensed","Arial Narrow",system-ui,sans-serif;')
s = s.replace('--f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;',
              '--f-body:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;')
s = s.replace('--f-mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;',
              '--f-mono:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;')
assert 'fonts.googleapis' not in s
s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
footer = f'''  <footer class="note">Progetto aperto: codice e dati su <a href="{REPO}" target="_blank" rel="noopener">GitHub</a>.
    Hai trovato un errore o manca un evento? <a href="{REPO}/issues/new?template=correzione.yml" target="_blank" rel="noopener">Segnalalo qui</a>.
    Gli scioperi sono aggiornati ogni giorno dal calendario del Ministero dei Trasporti; manifestazioni ed eventi eccezionali sono verificati a mano.
    Codice con licenza MIT, dati con licenza CC BY 4.0. Nessun cookie, nessun tracciamento.</footer>
</div>

<script>'''
assert s.count('</div>\n\n<script>') == 1
s = s.replace('</div>\n\n<script>', footer)
head = '''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<meta name="description" content="Mappa di scioperi, manifestazioni ed eventi eccezionali in Italia, con la fonte di ogni evento.">
'''
t = s.index('</title>') + len('</title>')
s = head + s[:t] + '\n' + s[t:]
e = s.index('</style>') + len('</style>')
s = s[:e] + '\n</head>\n<body>' + s[e:] + '\n</body>\n</html>\n'
(ROOT / "index.html").write_text(s, encoding="utf-8")
print(f"index.html: {len(d['eventi'])} eventi ({d['n_auto']} automatici dal MIT, {len(d['doppi'])} doppioni saltati)")
if d["da_verificare"]:
    print("ATTENZIONE: scioperi manuali con fonte MIT non più nel calendario (revocati?):", ", ".join(d["da_verificare"]))
