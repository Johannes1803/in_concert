"""This module contains setup shared between different testing frameworks.

These frameworks are:
- pytest for unit tests
- behave for bdd style testing/acceptance testing
"""
import http
import json


def get_bearer_token(settings_auth) -> dict:
    conn = http.client.HTTPSConnection(settings_auth.domain)
    payload_dict: dict = {
        "client_id": settings_auth.client_id,
        "client_secret": settings_auth.client_secret,
        "audience": settings_auth.audience,
        "grant_type": settings_auth.grant_type,
    }
    payload: str = json.dumps(payload_dict)
    headers = {"content-type": "application/json"}

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()
    data_decoded = data.decode("utf-8")
    data_dict = json.loads(data_decoded)
    return data_dict
