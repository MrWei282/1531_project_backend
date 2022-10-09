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
    channel_message_id = resp_dm_send.json()["message_id"]

    # create a dm
    resp_dm_create = requests.post(url + "dm/create/v1", json={
        "token": response_user_1_token,
        "u_ids": [response_user_2_id, response_user_3_id]
    })
    dm_id = resp_dm_create.json()["dm_id"]

    # send a message in that dm
    resp_dm_send = requests.post(url + "message/senddm/v1", json={
        "token": response_user_1_token,
        "dm_id": dm_id,
        "message": "valid message"
    })
    dm_message_id = resp_dm_send.json()["message_id"]

    values = {
        "token1": response_user_1_token,
        "message_id": channel_message_id,
        "dm_message_id": dm_message_id,
    }
    return values

# testing with invalid react_id, valid message_id
def test_invalid_react_id(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 123
    })
    assert response.status_code == 400
    
# testing with invalid react_id, valid message_id
def test_invalid_msg_id(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"]+100,
        "react_id": 123
    })
    assert response.status_code == 400

# checking to see if a single react can be viewed using dm_messages
def test_valid_react(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == 200

def test_user_already_reacted(data):

    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == 200

    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == 400
