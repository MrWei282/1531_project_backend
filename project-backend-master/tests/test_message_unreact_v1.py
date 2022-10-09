from src.config import url
import requests
import pytest

@pytest.fixture
def data():
    # clear used data
    requests.delete(url + 'clear/v1')

    # create users
    response_user_1 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z5343970@gmail.com", 
             "password": "czt20020128", 
             "name_first": "Zhitao",
             "name_last": "Chen"
        })
    response_user_1_token = response_user_1.json()['token']

    response_user_2 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z536@unsw.edu.au", 
             "password": "Aa!F@32(Bc", 
             "name_first": "Tianyu",
             "name_last": "Wei"
        })
    response_user_2_id = response_user_2.json()['auth_user_id']
    response_user_2_token = response_user_2.json()['token']

    response_user_3 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z123@unsw.edu.au", 
             "password": "abcdefg", 
             "name_first": "Andrew",
             "name_last": "Wei"
        })
    response_user_3_id = response_user_3.json()['auth_user_id']
    
    channel_response = requests.post(url + "channels/create/v2", json={
        "token":        response_user_1_token,
        "name":         "public_channel",
        "is_public":    True
    })
    channel_id = channel_response.json()["channel_id"]
    
    # send a message in that channel
    resp_dm_send = requests.post(url + "message/send/v1", json={
        "token": response_user_1_token,
        "channel_id": channel_id,
        "message": "valid message"
    })
    message_id = resp_dm_send.json()["message_id"]

    response = requests.post(url + "dm/create/v1", json={
        "token": response_user_1_token,
        "u_ids": [response_user_2_id, response_user_3_id]
    })
    dm_id = response.json()["dm_id"]

    response = requests.post(url + "message/senddm/v1", json={
        "token": response_user_1_token,
        "dm_id": dm_id,
        "message": "valid message"
    })
    message_id = response.json()["message_id"]

    requests.post(url + "message/react/v1", json={
        "token": response_user_1_token, 
        "message_id": message_id,
        "react_id": 1
    })

    values = {
        "token1": response_user_1_token,
        "token2": response_user_2_token,
        "message_id": message_id
    }
    return values

def test_invalid_message_id(data):
    response = requests.post(url + "message/unreact/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"]+100,
        "react_id": 1
    })
    assert response.status_code == 400

def test_invalid_react_id(data):
    response = requests.post(url + "message/unreact/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 123
    })
    assert response.status_code == 400

def test_valid_single_unreact(data):
    response = requests.post(url + "message/unreact/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == 200

def test_user_no_unreacted(data):
    response = requests.post(url + "message/unreact/v1", json={
        "token": data["token2"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == 400
