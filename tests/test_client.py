import pytest


import os
import logging

import pytest
from ttdapi.client import BaseTTDClient
import ttdapi.exceptions

LOGIN = os.environ['TTD_USERNAME']
PASSWORD = os.environ['TTD_PASSWORD']

@pytest.fixture
def fake_client():
    return BaseTTDClient(login='foo',
                         password="Nonexistent",
                         base_url="https://apisb.thetradedesk.com/v3/")

@pytest.fixture
def client():
    return BaseTTDClient(login=LOGIN,
                         password=PASSWORD,
                         base_url="https://apisb.thetradedesk.com/v3/")

def test_client_raises_config_error_on_wrong_credentials(fake_client):
    with pytest.raises(ttdapi.exceptions.TTDApiPermissionsError) as excinfo:
        fake_client.token

    assert "invalid credentials" in str(excinfo.value).lower()

def test_client_can_authenticate(client):
    old_token = client.token
    assert old_token is not None

    # assert that invoking the token again doesn't fetch a new one
    assert client.token == old_token

    # delete the token
    client.token = None
    # make sure we get a new one
    new_token = client.token
    assert new_token != old_token and new_token is not None

def test_building_urls(fake_client):
    fake_client.base_url = "api.com/v3/"
    tests = [
        ("/campaign/get", "api.com/v3/campaign/get"),
        ("campaign/get", "api.com/v3/campaign/get"),
        ("campaign/get", "api.com/v3/campaign/get"),
    ]
    for endpoint, expected in tests:
        assert fake_client._build_url(endpoint) == expected

def test_client_fails_on_unauthorized_resource(fake_client):
    endpoint = "category/industrycategories"
    fake_client.token = "INVALId"

    # this makes an authorized GET without retry on failed refresh_token
    # we use request("GET") because client.get is overriden
    resp = fake_client.request("GET", fake_client._build_url(endpoint))
    assert resp.status_code == 403
    assert "auth token is not valid or has expired" in resp.json()["Message"]

def test_client_refreshes_token_after_403_request(caplog, client):
    endpoint = "category/industrycategories"
    client.token = "INVALID"

    with caplog.at_level(logging.DEBUG):
        resp = client._request("GET", client._build_url(endpoint))

    assert "Token expired or invalid, trying again" in caplog.text
    # eventually succeeds after 1st try
    assert client.token is not None and client.token != "INVALID"
    assert resp.status_code == 200

    # next request reuses existing token
    resp2 = client._request("GET", client._build_url(endpoint))
    assert resp2.status_code == 200

def test_making_client_get_request_succeeds(client):
    endpoint = "category/industrycategories"
    data = client.get(endpoint)
    assert isinstance(data, dict)


def test_pagination(client):
    results = client.post_paginated(
        "advertiser/query/partner",
        json_payload={
            "Availabilities": ['Available', 'Archived'],
            'PartnerId': '304zmgy',
        },
        page_size= 1,
        page_start_index= 0
    )


    # we know there is at least one
    # and we hope we don't end up in an infinite cycle
    assert len(list(results)) > 0
