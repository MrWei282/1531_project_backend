import pytest
import requests
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
    user0_id = user0["auth_user_id"]

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
    user2_id = user2["auth_user_id"]

    public_channel_response = requests.post(config.url + "channels/create/v2", json={
        "token":        user1_token,
        "name":         "public_channel",
        "is_public":    True
    })
    public_channel_id = public_channel_response.json()["channel_id"]
    
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': user1_token,
        'channel_id': public_channel_id,
        'message': 'hello',
    })
    message_id1 = resp.json()['message_id']
    
    return {
        "user0_token":          user0_token,
        "user0_id":             user0_id,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "user2_id":             user2_id,
        "message_id1":          message_id1,
        "public_channel_id":    public_channel_id,
    }

# testing invalid token only
def test_message_remove_v1_invalid_token(data_setup):
    message_id = data_setup["message_id1"]
    response = requests.delete(config.url + "message/remove/v1", json={
        "token":        "hello",
        "message_id":   message_id,
    })
    assert response.status_code == 403

# testing valid token (user is a member), invalid message_id
def test_message_remove_v1_invalid_message_id(data_setup):
    user1_token = data_setup["user1_token"]
    response = requests.delete(config.url + "message/remove/v1", json={
        "token":        user1_token,
        "message_id":   -1234
    })
    assert response.status_code == 400

# testing invalid token and message_id
def test_message_remove_v1_invalid_token_and_message_id(data_setup):
    response = requests.delete(config.url + "message/remove/v1", json={
        "token":        "hello",
        "message_id":   -1234,
    })
    assert response.status_code == 403

def test_message_remove_v1_unauthorised_user(data_setup):
    user2_token = data_setup["user2_token"]
    message_id1 = data_setup["message_id1"]

    response1 = requests.delete(config.url + "message/remove/v1", json={
        "token":        user2_token,
        "message_id":   message_id1,
    })
    assert response1.status_code == 403

# testing normal
def test_message_remove_v1_normal_user_message_channel(data_setup):
    user1_token = data_setup["user1_token"]
    user2_id = data_setup["user2_id"]
    public_channel_id = data_setup["public_channel_id"]
    user2_token = data_setup["user2_token"]

    response1 = requests.post(config.url + "channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   public_channel_id,
        "u_id":         user2_id
    })
    assert response1.status_code == 200

    response2 = requests.post(config.url + "message/send/v1", json={
        "token":        user2_token,
        "channel_id":   public_channel_id,
        "message":      "hi?"
    })
    data2 = response2.json()
    message1_id = data2["message_id"]

    response4 = requests.delete(config.url + "message/remove/v1", json={
        "token":        user2_token,
        "message_id":   message1_id,
    })
    assert response4.status_code == 200

def test_message_remove_v1_normal_user_messages_dm(data_setup):
    user1_token = data_setup["user1_token"]
    user2_id = data_setup["user2_id"]
    user2_token = data_setup["user2_token"]

    response1 = requests.post(config.url + "dm/create/v1", json={
        "token":        user1_token,
        "u_ids":        [user2_id]
    })
    assert response1.status_code == 200
    dm_id = response1.json()["dm_id"]

    response2 = requests.post(config.url + "message/senddm/v1", json={
        "token":        user2_token,
        "dm_id":        dm_id,
        "message":      "hi?"
    })
    data2 = response2.json()
    message1_id = data2["message_id"]

    response4 = requests.delete(config.url + "message/remove/v1", json={
        "token":        user2_token,
        "message_id":   message1_id,
    })
    assert response4.status_code == 200

