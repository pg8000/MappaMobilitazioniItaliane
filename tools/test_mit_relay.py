import io
import json
import os
import unittest
from unittest.mock import patch

import mit_relay


class Response(io.BytesIO):
    def __init__(self, body, headers=None):
        super().__init__(body)
        self.headers = headers or {}


class RelayTests(unittest.TestCase):
    def test_uses_short_lived_github_identity_and_checks_source(self):
        requests = []

        def open_request(request, timeout):
            requests.append(request)
            if len(requests) == 1:
                return Response(json.dumps({"value": "signed-token"}).encode())
            return Response(b"x" * 1200, {"X-MIT-Source": "scioperi.mit.gov.it"})

        env = {
            "ACTIONS_ID_TOKEN_REQUEST_URL": "https://token.actions.githubusercontent.com/test?api-version=2.0",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token",
        }
        with patch.dict(os.environ, env), patch.object(mit_relay.urllib.request, "urlopen", side_effect=open_request):
            self.assertEqual(mit_relay.scarica_relay("rss", 2000), b"x" * 1200)
        self.assertIn("audience=https%3A%2F%2Fmit-relay-mappa-2026", requests[0].full_url)
        self.assertEqual(requests[1].full_url, mit_relay.RELAY_URL + "/rss")
        self.assertEqual(requests[1].get_header("Authorization"), "Bearer signed-token")

    def test_rejects_unexpected_path_without_a_request(self):
        with patch.object(mit_relay.urllib.request, "urlopen") as open_request:
            with self.assertRaises(ValueError):
                mit_relay.scarica_relay("https://other.example", 2000)
            open_request.assert_not_called()


if __name__ == "__main__":
    unittest.main()

