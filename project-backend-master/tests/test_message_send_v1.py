import pytest
import requests
import json
from src import config

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
    public_channel = public_channel_response.json()
    public_channel_id = public_channel["channel_id"]

    return {
        "user0_token":          user0_token,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "public_channel_id":    public_channel_id,
    }

# testing invalid channel_id
def test_message_send_v1_invalid_channel_id(data_setup):
    user1_token = data_setup["user1_token"]
    response = requests.post(config.url + "message/send/v1", json={
        "token":        user1_token,
        "channel_id":   -123,
        "message":      "hello"
    })
    assert response.status_code == 400

# testing invalid token
def test_message_send_v1_invalid_token(data_setup):
    public_channel = data_setup["public_channel_id"]
    response = requests.post(config.url + "message/send/v1", json={
        "token":        "kjkjd",
        "channel_id":   public_channel,
        "message":      "hello"
    })
    assert response.status_code == 403

def test_message_send_v1_unauthorised_user(data_setup):
    user2_token = data_setup["user2_token"]
    public_channel = data_setup["public_channel_id"]

    response1 = requests.post(config.url + "message/send/v1", json={
        "token":        user2_token,
        "channel_id":   public_channel,
        "message":      "hello"
    })

    assert response1.status_code == 403

# token and channel_id both invalid
def test_message_send_v1_invalid_token_and_channel_id(data_setup):
    response = requests.post(config.url + "message/send/v1", json={
        "token":        "1234",
        "channel_id":   -1234,
        "message":      "hello"
    })
    assert response.status_code == 403

# invalid message
def test_message_send_v1_invalid_message(data_setup):
    user1_token = data_setup["user1_token"]
    public_channel = data_setup["public_channel_id"]

    response1 = requests.post(config.url + "message/send/v1", json={
        "token":        user1_token,
        "channel_id":   public_channel,
        "message":      ""
    })

    response2 = requests.post(config.url + "message/send/v1", json={
        "token":        user1_token,
        "channel_id":   public_channel,
        "message":      "hi"*1001
    })

    assert response1.status_code == 400
    assert response2.status_code == 400

def test_message_send_v1(data_setup):
    user1_token = data_setup["user1_token"]
    public_channel = data_setup["public_channel_id"]

    response = requests.post(config.url + "message/send/v1", json={
        "token": user1_token,
        "channel_id": public_channel,
        "message": "Send a message from the authorised user to the channel specified by channel_id."
    })
    response.status_code == 200

    response = requests.get(config.url + "channel/messages/v2", params={
        "token": user1_token,
        "channel_id": public_channel,
        "start": 0
    })
    response.status_code == 200
