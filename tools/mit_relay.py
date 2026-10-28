"""Accesso al relay MIT tramite identità temporanea di GitHub Actions."""

import json
import os
import time
import urllib.parse
import urllib.request

RELAY_URL = "https://mit-relay-mappa-2026.heartyfawn37.chatgpt.site"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"


def oidc_token():
    request_url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    request_token = os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]
    separator = "&" if "?" in request_url else "?"
    url = request_url + separator + "audience=" + urllib.parse.quote(RELAY_URL, safe="")
    request = urllib.request.Request(
        url, headers={"Authorization": "bearer " + request_token,
                      "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=10) as response:
        token = json.load(response)["value"]
    if not isinstance(token, str) or len(token) > 16000:
        raise ValueError("Token GitHub OIDC non valido")
    return token


def scarica_relay(path, limit):
    if path not in ("annual", "rss"):
        raise ValueError("Percorso relay non consentito")
    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(
                RELAY_URL + "/" + path,
                headers={"Authorization": "Bearer " + oidc_token(),
                         "Accept": "text/html, application/rss+xml",
                         "User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=45) as response:
                if response.headers.get("X-MIT-Source") != "scioperi.mit.gov.it":
                    raise ValueError("Provenienza relay non riconosciuta")
                content = response.read(limit + 1)
            if len(content) > limit or len(content) < 1000:
                raise ValueError("Dimensione risposta relay non valida")
            return content
        except (OSError, TimeoutError, ValueError, KeyError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(attempt + 1)
    raise RuntimeError(f"Relay MIT non disponibile: {last_error}")

