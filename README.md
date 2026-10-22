# Piazze e scioperi d'Italia

Mappa di scioperi proclamati e manifestazioni annunciate in Italia, con gli eventi eccezionali
(manifestazioni non preavvisate o vietate, scontri) segnalati come tali. Ogni evento riporta la fonte.

**Sito:** https://pg8000.github.io/MappaMobilitazioniItaliane/

## Cosa contiene

| Percorso | Cosa è |
| --- | --- |
| `index.html` | La pagina pubblicata: un solo file, senza dipendenze esterne, senza cookie né tracciamento |
| `data/eventi.json` | Gli stessi dati in formato JSON, riutilizzabili (licenza CC BY 4.0) |
| `docs/PIANO.md` | Piano del progetto, con i criteri di inclusione degli eventi |
| `docs/RICERCA-E-FONTI.md` | Fonti consultate, eventi esclusi e motivazioni |
| `tools/build_page.py` | Rigenera `index.html` dal sorgente di lavoro (`tools/sorgente-artifact.html`) |

## Criteri

- Solo eventi in Italia con data certa, luogo, promotore (o "non identificato") e almeno una fonte apribile.
- Scioperi verificati sul [calendario del Ministero dei Trasporti](https://scioperi.mit.gov.it/mit2/public/scioperi) quando vi compaiono.
- Descrizioni brevi e neutre; nessun nome di persone, nessun numero di feriti, fermati o partecipanti.

## Segnalare un errore

Usa il pulsante "Segnalalo qui" in fondo alla pagina o apri una [segnalazione](../../issues/new?template=correzione.yml).
Serve sempre il link a una fonte.

## Aggiornare la mappa

1. Modifica l'elenco `EVENTS` in `tools/sorgente-artifact.html` e la data "Dati aggiornati al".
2. Rigenera la pagina: `python tools/build_page.py tools/sorgente-artifact.html index.html https://github.com/pg8000/MappaMobilitazioniItaliane`
3. Carica i file modificati: GitHub Pages pubblica da solo in un paio di minuti.

## Licenze

Codice: MIT (`LICENSE`). Dati: CC BY 4.0 (`LICENSE-DATI.md`).
