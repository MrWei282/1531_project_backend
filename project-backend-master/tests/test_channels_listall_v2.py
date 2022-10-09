'''test file for channel listall'''
import pytest
import requests

from src.config import url

@pytest.fixture
def initialise():
    requests.delete(f"{url}/clear/v1")
    
    resp_user_1 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z5343970@gmail.com", 
             "password": "czt20020128", 
             "name_first": "Zhitao",
             "name_last": "Chen"
        })
    
    return resp_user_1.json()['token']

def test_single_channel(initialise):
    '''testing for single channel'''

    requests.post(
        f"{url}/channels/create/v2", json = {
            "token": initialise,
            "name": "channel_7",
            "is_public": True
        })

    resp_listall_pub = requests.get(
        f"{url}/channels/listall/v2", params = {
            "token": initialise
        })
    assert resp_listall_pub.status_code == 200
    assert resp_listall_pub.json()["channels"] == [{"channel_id": 1, "name": "channel_7"}]


def test_single_private_channel(initialise):
    '''testing single private channel'''

    requests.post(
        f"{url}/channels/create/v2", json = {
            "token": initialise,
            "name": "channel_9",
            "is_public": False
        })

    resp_listall_pri = requests.get(
        f"{url}/channels/listall/v2", params = {
            "token": initialise
        })
    assert resp_listall_pri.status_code == 200
    assert resp_listall_pri.json()["channels"] == [{"channel_id": 1, "name": "channel_9"}]


def test_multiple_channel(initialise):
    '''testing multiple channel'''

    requests.post(
        f"{url}/channels/create/v2", json = {
            "token": initialise,
            "name": "channel_7",
            "is_public": True
        })
    
    requests.post(
        f"{url}/channels/create/v2", json = {
            "token": initialise,
            "name": "channel_9",
            "is_public": True
        })
    
    requests.post(
        f"{url}/channels/create/v2", json = {
            "token": initialise,
            "name": "club_420",
            "is_public": False
        })

    resp_listall_mul = requests.get(
        f"{url}/channels/listall/v2", params = {
            "token": initialise
        })
    assert resp_listall_mul.status_code == 200
    assert resp_listall_mul.json()["channels"] == [{"channel_id": 1, "name": "channel_7"},
                                                   {"channel_id": 2, "name": "channel_9"},
                                                   {"channel_id": 3, "name": "club_420"},]

def test_no_channel(initialise):
    '''no channal exit'''

    resp_listall_none = requests.get(
        f"{url}/channels/listall/v2", params = {
            "token": initialise
        })
    assert resp_listall_none.status_code == 200
    assert resp_listall_none.json()["channels"] == []

def test_invalid_token(initialise):
    '''To check the raise error functionailty for invalid token.'''

    resp_1 = requests.get(
        f"{url}/channels/listall/v2", params = {
            "token": "invalid_token"
        })
    assert resp_1.status_code == 403

    resp_2 = requests.get(
        f"{url}/channels/listall/v2", params = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjF9.GUPqQ_DOSzE4aXkV7C8gnNCmf-V1ti5agmqq0moBtdw"
        })
    assert resp_2.status_code == 403
