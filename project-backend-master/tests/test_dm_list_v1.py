import pytest
import json
import requests
from src import config


def test_dm_list():
    assert requests.delete(config.url+'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': '1@mail.com',
        'password': 'abc123',
        'name_first': 'one',
        'name_last': 'two',
    })
    assert resp.status_code == 200
    owner1 = resp.json()
    resp = requests.post(config.url+'dm/create/v1', json={
        'token': owner1['token'],
        'u_ids': [],
    })
    assert resp.status_code == 200
    resp = requests.post(config.url+'dm/create/v1', json={
        'token': owner1['token'],
        'u_ids': [],
    })
    assert resp.status_code == 200
    resp = requests.get(config.url + 'dm/list/v1', params={
        'token': owner1['token'],
    })
    assert resp.status_code == 200


def test_dm_list_invalid_token():
    assert requests.delete(config.url+'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': '1@gmail.com',
        'password': 'abc123',
        'name_first': 'one',
        'name_last': 'one',
    })
    assert resp.status_code == 200
    owner1 = resp.json()
    resp = requests.post(config.url+'dm/create/v1', json={
        'token': owner1['token'],
        'u_ids': [],
    })
    assert resp.status_code == 200
    resp = requests.get(config.url+'dm/list/v1', params={
        'token': 1,
        'u_ids': [],
    })
    assert resp.status_code == 403
