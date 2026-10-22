#!/usr/bin/env python3
"""Approva una proposta: legge il blocco JSON dalla issue (evento GitHub) e aggiunge l'evento a data/eventi.json.
Gli eventi eccezionali (campo "exc") non si approvano da qui: si inseriscono sempre a mano.
Scrive il messaggio per la issue in $MSG_FILE (default /tmp/approva-msg.txt). Esce con 1 se non approva."""
import hashlib, json, os, re, sys
from comuni import carica, salva, oggi, province
from valida import errori_evento

MSG = os.environ.get("MSG_FILE", "/tmp/approva-msg.txt")
ORDINE = ["id", "orgs", "type", "scope", "sector", "place", "area", "start", "end", "time", "title", "who", "where", "tbc", "pending", "src"]


def rifiuta(testo):
    open(MSG, "w", encoding="utf-8").write(testo)
    print(testo)
    sys.exit(1)


def main():
    ev_path = os.environ.get("GITHUB_EVENT_PATH") or sys.argv[1]
    issue = json.load(open(ev_path, encoding="utf-8"))["issue"]
    m = re.search(r"```json\s*(\{.*?\})\s*```", issue.get("body") or "", re.S)
    if not m:
        rifiuta("Non trovo il blocco JSON nella issue. Ripristinalo e riapplica l'etichetta `approva`.")
    try:
        p = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        rifiuta(f"Il JSON non è valido ({e}). Correggilo e riapplica l'etichetta `approva`.")
    if "exc" in p:
        rifiuta("Gli eventi eccezionali non si approvano da qui: vanno inseriti a mano in `data/eventi.json` "
                "con la nota e le fonti (vedi docs/AUTOMAZIONE.md).")
    base, prov = carica("eventi.json"), province()
    f = p.get("fonte") or {}
    if not str(f.get("url", "")).startswith("https://") or not f.get("nome"):
        rifiuta("Serve `fonte` con `nome` e `url` https.")
    chiave = "n-" + hashlib.sha1(f["url"].encode()).hexdigest()[:8]
    base["fonti"].setdefault(chiave, {"nome": str(f["nome"])[:80], "url": f["url"]})
    p.setdefault("end", p.get("start"))
    p["type"] = "manifestazione"
    p["orgs"] = p.get("orgs") or ["non-identificato"]
    p["src"] = [chiave]
    if not p.get("id"):
        p["id"] = f"{p.get('place', 'it')}-{str(p.get('start', ''))[5:]}-{chiave[2:6]}"
    luoghi = dict(base["luoghi"])
    if p.get("place") and p["place"] not in luoghi and p["place"] in prov:
        luoghi[p["place"]] = prov[p["place"]]
    ev = {k: p[k] for k in ORDINE if p.get(k) not in (None, "", [])}
    err = errori_evento(ev, base, luoghi)
    if any(x["id"] == ev.get("id") for x in base["eventi"]):
        err.append("esiste già un evento con questo id")
    if err:
        rifiuta("Non posso approvare, ci sono problemi:\n\n" + "\n".join(f"- {x}" for x in err) +
                "\n\nModifica il JSON nella issue e riapplica l'etichetta `approva`.")
    base["luoghi"] = luoghi
    base["eventi"].append(ev)
    base["snapshot"] = oggi().isoformat()
    salva("eventi.json", base)
    open(MSG, "w", encoding="utf-8").write(f"Approvata: aggiunta `{ev['id']}` a `data/eventi.json`. La pagina si aggiorna entro un paio di minuti.")
    print("approvata", ev["id"])


if __name__ == "__main__":
    main()
