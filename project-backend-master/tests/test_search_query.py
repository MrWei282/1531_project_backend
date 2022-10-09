import pytest
import requests
import json
import string 
import random
from src import config
from src.error import AccessError, InputError
from tests.test_dm_message_v1 import dm_id

@pytest.fixture
def data_setup():
    requests.delete(config.url + "clear/v1")
    user0_response = requests.post(config.url + "auth/register/v2", json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    user0 = user0_response.json()
    user0_token = user0["token"]
    user1_response = requests.post(config.url + "auth/register/v2", json={
       'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    user1 = user1_response.json()
    user1_token = user1["token"]
    user2_response = requests.post(config.url + "auth/register/v2", json={
        'email' : 'czt2@gmail.com','password' : 'czt0128',
        'name_first' : 'linbo','name_last' : 'chen'
    })
    user2 = user2_response.json()
    user2_token = user2["token"]

    public_channel_response = requests.post(config.url + "channels/create/v2", json={
        "token":        user1_token,
        "name":         "public_channel",
        "is_public":    True
    })
    requests.post(config.url + "channels/create/v2", json={
        "token":        user2_token,
        "name":         "public_channel2",
        "is_public":    True
    })
    requests.post(config.url + "channels/create/v2", json={
        "token":        user1_token,
        "name":         "public_channeld2",
        "is_public":    True
    })
    other2 = requests.post(config.url + "channels/create/v2", json={
        "token":        user1_token,
        "name":         "public_channeld2",
        "is_public":    True
    })
    third_ch_id = other2.json()["channel_id"]
    public_channel = public_channel_response.json()
    public_channel_id = public_channel["channel_id"]

    requests.post(config.url + "message/send/v1", json={
        "token":        user1_token,
        "channel_id":   public_channel_id,
        "message":      "hello world n***s in paris yeee"
    })
    requests.post(config.url + "message/send/v1", json={
        "token":        user2_token,
        "channel_id":   public_channel_id,
        "message":      "hello world n***s in paris 2yeee"
    })
    requests.post(config.url + "message/send/v1", json={
        "token":        user1_token,
        "channel_id":   public_channel_id,
        "message":      "hello world ufff  yeee"
    })
    requests.post(config.url + "message/send/v1", json={
        "token":        user1_token,
        "channel_id":   third_ch_id,
        "message":      "hello world ufff  efersdfyeee"
    })
    re_dm = requests.post(config.url + 'dm/create/v1',
        json={'token': user1_token, 'u_ids': [user2['auth_user_id']]})
    dm_id = re_dm.json()
    requests.post(config.url + 'dm/create/v1',
        json={'token': user2_token, 'u_ids': []})

    te = requests.post(config.url + 'message/senddm/v1', json={
        'token': user1_token,
        'dm_id': dm_id['dm_id'],
        'message': 'Hello I am testing query in paris ',
    })
    requests.post(config.url + 'message/senddm/v1', json={
        'token': user1_token,
        'dm_id': dm_id['dm_id'],
        'message': 'Hello I am testing query ',
    })
    assert te.status_code == 200
    return {
        "user0_token":          user0_token,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "public_channel_id":    public_channel_id,
    }

def test_easy_query(data_setup):
    response = requests.get(config.url + "search/v1", params={
        'token': data_setup['user1_token'],
        'query_str': 'paris'
    })
    assert response.status_code == 200
    assert len(response.json()['messages']) == 2
    

def test_invalid_token():
    response = requests.get(config.url + "search/v1", params={
        'token': 'user0_token_inva',
        'query_str': 'paris'
    })

    assert response.status_code == AccessError.code

def test_incorrect_lenght(data_setup):
    query_0 = ''
    query_1001 = ''.join((random.choice(string.ascii_uppercase) for x in range(1001)))

    response1 = requests.get(config.url + "search/v1", params={
        'token': data_setup['user0_token'],
        'query_str': query_1001
    })
    response = requests.get(config.url + "search/v1", params={
        'token': data_setup['user0_token'],
        'query_str': query_0
    })
    assert response.status_code == InputError.code
    assert response1.status_code == InputError.code




