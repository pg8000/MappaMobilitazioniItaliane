"""Ambiti amministrativi espliciti: nessuna geolocalizzazione dedotta dal titolo."""
from comuni import slug, REGIONI

PROVINCE_REGIONI = {
    "Abruzzo": "Chieti|L'Aquila|Pescara|Teramo",
    "Basilicata": "Matera|Potenza",
    "Calabria": "Catanzaro|Cosenza|Crotone|Reggio Calabria|Vibo Valentia",
    "Campania": "Avellino|Benevento|Caserta|Napoli|Salerno",
    "Emilia-Romagna": "Bologna|Ferrara|Forlì-Cesena|Modena|Parma|Piacenza|Ravenna|Reggio Emilia|Rimini",
    "Friuli-Venezia Giulia": "Gorizia|Pordenone|Trieste|Udine",
    "Lazio": "Frosinone|Latina|Rieti|Roma|Viterbo",
    "Liguria": "Genova|Imperia|La Spezia|Savona",
    "Lombardia": "Bergamo|Brescia|Como|Cremona|Lecco|Lodi|Mantova|Milano|Monza e Brianza|Pavia|Sondrio|Varese",
    "Marche": "Ancona|Ascoli Piceno|Fermo|Macerata|Pesaro e Urbino",
    "Molise": "Campobasso|Isernia",
    "Piemonte": "Alessandria|Asti|Biella|Cuneo|Novara|Torino|Verbano-Cusio-Ossola|Vercelli",
    "Puglia": "Bari|Barletta-Andria-Trani|Brindisi|Foggia|Lecce|Taranto",
    "Sardegna": "Cagliari|Nuoro|Oristano|Sassari|Sud Sardegna",
    "Sicilia": "Agrigento|Caltanissetta|Catania|Enna|Messina|Palermo|Ragusa|Siracusa|Trapani",
    "Toscana": "Arezzo|Firenze|Grosseto|Livorno|Lucca|Massa-Carrara|Pisa|Pistoia|Prato|Siena",
    "Trentino-Alto Adige": "Bolzano|Trento",
    "Umbria": "Perugia|Terni",
    "Valle d'Aosta": "Aosta",
    "Veneto": "Belluno|Padova|Rovigo|Treviso|Venezia|Verona|Vicenza",
}
LUOGHI_REGIONI = {slug(p): [r] for r, names in PROVINCE_REGIONI.items() for p in names.split('|')}
LUOGHI_REGIONI.update({"malpensa": ["Lombardia"], "sandona": ["Veneto"],
                       "grottammare": ["Marche"], "a1": ["Toscana", "Emilia-Romagna"]})


def arricchisci(luoghi, eventi):
    for key, place in luoghi.items():
        region = place.get("region")
        place["regions"] = [region] if region in REGIONI else LUOGHI_REGIONI.get(key, [])
    for event in eventi:
        if event.get("scope") == "nazionale":
            event["regions"] = []
            continue
        regions = list(luoghi.get(event.get("place"), {}).get("regions", []))
        raw = slug(event.get("source_region", "")).replace('-', '')
        regions += [r for r in REGIONI if slug(r).replace('-', '') == raw]
        event["regions"] = sorted(set(regions))
