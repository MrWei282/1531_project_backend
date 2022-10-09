import pytest
import requests
import json
from src import config
from datetime import datetime
from time import sleep
def test_message_senddm():
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    resp = requests.post(config.url + 'auth/register/v2', json={
       'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user1 = resp.json()

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user2 = resp.json()

    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'],
        'u_ids': [user2['auth_user_id']],
    })
    assert resp.status_code == 200
    dm_id1 = resp.json()['dm_id']

    resp = requests.post(config.url + 'message/senddm/v1', json={
        'token': user1['token'],
        'dm_id': dm_id1,
        'message': 'Hello World!',
    })
    assert resp.status_code == 200

def test_message_senddm_length_bigger():
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    resp = requests.post(config.url + 'auth/register/v2', json={
       'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user1 = resp.json()

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user2 = resp.json()

    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'],
        'u_ids': [user2['auth_user_id']],
    })
    assert resp.status_code == 200
    dm_id1 = resp.json()['dm_id']

    resp = requests.post(config.url + 'message/senddm/v1', json={
        'token': user1['token'],
        'dm_id': dm_id1,
        'message': 1001*'h',
    })
    assert resp.status_code == 400

def test_message_senddm_invaild_user():
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user1 = resp.json()

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user2 = resp.json()

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt2@gmail.com','password' : 'czt0128',
        'name_first' : 'linbo','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user3 = resp.json()

    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'],
        'u_ids': [user2['auth_user_id']],
    })
    assert resp.status_code == 200
    dm_id1 = resp.json()['dm_id']

    resp = requests.post(config.url + 'message/senddm/v1', json={
        'token': user3['token'],
        'dm_id': dm_id1,
        'message': 'hehexd',
    })
    assert resp.status_code == 403