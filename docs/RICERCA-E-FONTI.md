# Recupero dell’archivio annuale — 22 ottobre 2026

Fonte primaria aperta e scaricata direttamente: https://scioperi.mit.gov.it/mit2/public/scioperi/ricerca . Il form dichiara che lo storico parte dal 2014 e consente di includere effettuati e revocati.

Richiesta POST: `dataInizio=01/01/2026`, `dataFine=31/12/2026`, `stato=0`, `settore=0`, `rilevanza=0`, categoria/sindacato vuoti. Risposta iniziale: **494 righe**, 328 effettuate, 26 in programma e 140 revocate; distribuite in tutti i 12 mesi. Sono mantenute le dichiarazioni distinte per proclamazione/ricezione, anche con data e sigle coincidenti. Il file generato conserva categoria originale, sindacati, territorio, date di proclamazione/ricezione, note e data di verifica.

Non si usa più il solo prospetto dei prossimi scioperi. Le vecchie 21 schede manuali con fonte MIT sono mantenute nel file curato per riferimento, ma non sommate alle righe ufficiali. La prima pagina annuale contiene **509 voci**: 494 ufficiali e 15 curate indipendentemente. Il conteggio normale esclude le 140 revoche.

Limiti: questo recupero non costituisce un censimento retrospettivo di ogni manifestazione del 2026, né può anticipare eventi non ancora annunciati. L’assenza di voci in una categoria non significa assenza di iniziative. La pagina rende esplicita questa distinzione.

---

## Registro precedente (conservato)

# Registro della ricerca (22 ottobre 2026, aggiornato alla v1.1)

Pagine aperte e lette per costruire il dataset. Le chiavi tra parentesi sono quelle usate in `SRC` / `data/eventi.json`.

## Fonti usate

| Chiave | Fonte | Cosa ha fornito |
| --- | --- | --- |
| meteo | https://www.meteo.it/notizie/scioperi-novembre-2026-calendario-treni-aerei-e-mezzi-pubblici-6ad722d5 (20/10/2026) | Calendario scioperi di novembre con sigle sindacali |
| studenti | https://www.studenti.it/scioperi-novembre-2026-date-orari.html (19/10/2026) | Calendario novembre, controllo incrociato con Meteo.it |
| canale10 | https://canaledieci.it/2026/10/19/scioperi-novembre-2026-a-roma-e-nel-lazio-le-date-i-trasporti-coinvolti-e-gli-stop-nazionali/ | Sciopero commercio Lazio 1/11, nazionali di novembre |
| virgilio | https://www.virgilio.it/motori/info-utili/scioperi/sciopero-trasporti-date-orari-citta-ottobre-2026/350069/ | Scioperi trasporti 22–31 ottobre città per città |
| scioperometro | https://scioperometro.it/scioperi-ottobre-2026 | Controllo incrociato ottobre; La Lucente aeroporto Bologna 29/10 |
| scuolainf | https://www.scuolainforma.news/scioperi-dal-20-al-25-ottobre-2026-nessuno-stop-nella-scuola-ma-attenzione-ai-trasporti/ | FSE Bari e Anffas Grottammare 23/10 |
| lentepa | https://lentepubblica.it/cittadini-e-imprese/sciopero-generale-30-ottobre-scuole-treni-e-ospedali-ecco-chi-si-ferma/ | Sciopero generale 30/10: proclamanti, orari per settore |
| usb | https://www.usb.it/leggi-notizia/30-ottobre-e-sciopero-generale-0817.html | Comunicato USB sciopero generale |
| usbRoma | https://www.usb.it/leggi-notizia/sciopero-generale-30-ottobre-a-roma-appuntamento-ore-1030-piazza-dei-cinquecento-1634.html | Piazza USB a Roma, 30/10 ore 10:30 |
| ferrovie | https://www.ferrovie.info/treni-reali/sciopero-treni-29-e-30-ottobre-2026-a-rischio-alta-velocita-intercity-regionali-e-trenord.html | Orari sciopero treni 29–30/10 |
| qlazio | https://www.ilquotidianodellazio.it/roma-sabato-24-ottobre-cortei-e-proteste-attesi-10mila-manifestanti-strade-chiuse-e-bus-deviati.html | Cortei a Roma del 24/10 con percorsi e orari |
| ansaScuola | https://www.ansa.it/canale_legalita_scuola/notizie/2026/10/19/le-prossime-date-calde-il-30-ottobre-ancora-in-piazza_2a60599a-28a3-4e27-aa23-4fad27a4ecf3.html | Mobilitazioni studentesche 24/10, 30/10, 20/11 |
| studentiDate | https://www.studenti.it/scioperi-scuola-studenti-date-calde-ottobre-novembre-2026.html (20/10/2026) | Sciopero studentesco 20/11 e adesioni |
| ansaCgil | https://www.ansa.it/sito/notizie/politica/2026/10/17/cgil-in-piazza-siamo-100mila-il-20-novembre-sciopero-generale_c4547ea9-f018-4e78-adda-67ad7af8e7d0.html | Annuncio sciopero generale CGIL 20/11 (modalità non ancora formalizzate) |

## Fonti aggiunte nella v1.1

| Chiave | Fonte | Cosa ha fornito |
| --- | --- | --- |
| mit | https://scioperi.mit.gov.it/mit2/public/scioperi (prospetto al 22/10/2026) | Verifica di tutti gli scioperi dei trasporti, esclusioni per sigla del 30/10, CGIL 20/11 |
| fanpage | https://www.fanpage.it/roma/roma-sabato-di-cortei-e-proteste-confermata-la-manifestazione-ai-fori-incognita-circo-massimo/ | Roma 24/10: cortei confermati, Circo Massimo senza richiesta |
| ansa16 | https://ansa.it/sito/notizie/cronaca/2026/10/16/gli-studenti-in-piazza-cortei-in-tutta-italia.-a-torino-lancio-di-sassi-contro_1e152b63-e67e-4efd-9ec7-0ca3507f55e3.html | Torino 16/10, corteo non preavvisato con scontri |
| ilpost17 | https://www.ilpost.it/2026/10/17/scontri-milano-manifestazione-carovita/ | Milano 17/10 |
| ilpost19 | https://www.ilpost.it/2026/10/19/milano-devastazioni-saccheggi-scontri-negozi-polizia-manifestazione/ | Milano 17 e 18/10, cifre di polizia |
| tgcom17 | https://www.tgcom24.mediaset.it/cronaca/cortei-italia-in-piazza-sabato-17-ottobre-milano-genova-bologna-roma-torino_117789892-202602k.shtml | 17/10 città per città |
| sky18 | https://tg24.sky.it/cronaca/2026/10/18/scontri-guerriglia-milano-torino-bologna-cosa-e-successo | Bilanci 17/10 di Milano, Torino, Bologna, Bergamo |
| ansa18 | https://www.ansa.it/sito/notizie/cronaca/2026/10/18/centinaia-di-giovani-a-gruppetti-in-piazza-duomo-50-portati-in-questura_57da2060-1834-4ed4-a7a9-19a0843c94bd.html | Milano 18/10 |
| giorno22 | https://www.ilgiorno.it/milano/cronaca/sala-timori-scontri-sabato-ajsaaid3 | Milano: corteo anarchico non preavvisato e possibile divieto per il Blocco Studentesco |

Ricerca di eventi eccezionali tra il 1° e il 15 ottobre: nessun episodio in Italia trovato con fonte nazionale. Il corteo per Fakir a Pisa (non preavvisato) è del 21 luglio, quindi fuori periodo. Il corteo non preavvisato a Trieste segnalato da TriestePrima non è stato leggibile ed è escluso.

## Pagine non raggiungibili durante la ricerca

today.it (errore client), ilmattino.it e leggo.it (robots), sciopero.net (errore client), cgil.it calendario settimanale (errore client). Nella v1 il calendario MIT non era stato letto direttamente; nella v1.1 tutti gli scioperi dei trasporti sono stati confrontati con il prospetto MIT del 22/10 (vedi `RISPOSTA-REVIEW.md`).

## Eventi esclusi e perché

| Evento | Motivo |
| --- | --- |
| Presidio in Piazza Santi Apostoli, Roma, 24/10 ore 13:30 | Organizzatore e tema non indicati dalla fonte |
| La Lucente, aeroporto di Bologna, 29/10 (v1.1) | Non presente nel calendario MIT al 22/10; promotori non confermati |
| Genova e Brescia, 17/10 | Manifestazioni senza scontri riportati: non sono eventi eccezionali e sono fuori dal periodo ordinario |
| Roma e Bologna, 16/10 | Tensioni minori riportate da ANSA, senza scontri o mancato preavviso documentati |
| Assemblea studentesca a Roma, 23/10 | Assemblea, fuori scope (non è una manifestazione pubblica) |
| Corteo USB a Brescia, 30/10 | Unica fonte trovata non giornalistica, non aperta |
| Cortei del 20/11 in città specifiche | Città non ancora annunciate: lo sciopero è nella fascia nazionale |

## Scelte di posizionamento

- Air Campania (28/10): segnato su Napoli; l'azienda opera su scala regionale.
- ATVO (13/11): segnato su San Donà di Piave, sede dell'area servita, non sul centro storico di Venezia.
- Sciopero A1 GSA (27/10): punto a metà della tratta Incisa–Sasso Marconi (circa Barberino di Mugello).
- Toscana Aeroporti (30/10): un solo punto su Pisa, la scheda cita anche Firenze.
- Sciopero generale regionale USI-CIT Toscana (30/10): punto su Firenze, ambito "regionale".
