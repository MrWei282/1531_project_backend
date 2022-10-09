import pytest
import requests
from src.config import url

@pytest.fixture
def data():
    requests.delete(url + 'clear/v1')

    response1 = requests.post(url + "auth/register/v2", 
    json={
        "email": "czt1@aniston.com",
        "password": "abc1234",
        "name_first": "zhitao",
        "name_last": "chen"
    })
    token1 = response1.json()["token"]

    response2 = requests.post(url + "auth/register/v2", 
    json={
        "email": "czt2@aniston.com",
        "password": "abc1234",
        "name_first": "linbo",
        "name_last": "chen"
    })
    token2 = response2.json()["token"]
    user2_id = response2.json()["auth_user_id"]

    response3 = requests.post(url + "auth/register/v2", 
    json={
        "email": "czt3@aniston.com",
        "password": "abc1234",
        "name_first": "tianyu",
        "name_last": "chen"
    })
    token3 = response3.json()["token"]
    user3_id = response3.json()["auth_user_id"]

    response = requests.post(url + "dm/create/v1", 
    json={
        "token": token1,
        "u_ids": [user2_id]
    })
    dm_id = response.json()["dm_id"]

    channel_response = requests.post(url + "channels/create/v2", 
    json={
        "token":        token2,
        "name":         "Jennifer garner",
        "is_public":    True
    })
    assert channel_response.status_code == 200
    channel_id = channel_response.json()["channel_id"]

    add_user_channel_resp = requests.post(url + 'channel/invite/v2', 
    json={
        "token": token2, 
        "channel_id": channel_id, 
        "u_id": user3_id
    }) 
    assert add_user_channel_resp.status_code == 200

    channel_msg_resp = requests.post(url + "message/send/v1", 
    json={
        "token": token3,
        "channel_id": channel_id,
        "message": "Send this message or you die"
    })
    assert channel_msg_resp.status_code == 200
    channel_message_id = channel_msg_resp.json()["message_id"]

    dm_msg_resp = response = requests.post(url + "message/senddm/v1", 
    json={
        "token":        token2,
        "dm_id":        dm_id,
        "message":      "hello from the other side"
    })
    assert dm_msg_resp.status_code == 200
    dm_message_id = dm_msg_resp.json()["message_id"]

    return {
        "token1": token1,
        "token2": token2,
        "token3": token3,
        "user2_id" : user2_id,
        "dm_id": dm_id,
        "channel_id" : channel_id,
        "channel_message_id" : channel_message_id,
        "dm_message_id" : dm_message_id
    }


# testing invalid token
def test_message_share_invalid_token(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":                "czt",
        "og_message_id" :       data["dm_message_id"],
        "message" :             "hello",
        "channel_id":           data["channel_id"],
        "dm_id" :               -1
    })
    assert response.status_code == 403

# testing when neither dm_id nor channel id is -1
def test_message_share_valid_ids(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":                data["token2"],
        "og_message_id" :       data["channel_message_id"],
        "message" :             "hello",
        "channel_id":           data["channel_id"],
        "dm_id" :               data["dm_id"]
    })
    assert response.status_code == 400

#testing when sharing a message to a channel, user is not part of
def test_message_share_invalid_channelid(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":                data["token2"],
        "og_message_id" :       data["dm_message_id"],
        "message" :             "hello",
        "channel_id":           -1,
        "dm_id" :               data["dm_id"]
    })
    assert response.status_code == 403

#testing when sharing a message to a dm, user is not part of
def test_message_share_invalid_dmid(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":                data["token3"],
        "og_message_id" :       data["channel_message_id"],
        "message" :             "hello",
        "channel_id":           data["channel_id"],
        "dm_id" :               -1
    })
    assert response.status_code == 403

# testing invalid channel
def test_message_share_invalid_channel(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token2"],
        "og_message_id":    data["dm_message_id"],
        "message" :         "hello",
        "channel_id":       1381830,
        "dm_id" :           -1
    })
    assert response.status_code == 400

# testing invalid dm
def test_message_share_invalid_dm(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token2"],
        "og_message_id":    data["dm_message_id"],
        "message" :         "hello",
        "channel_id":       -1,
        "dm_id" :           9281739
    })
    assert response.status_code == 400

#testing when both channel id and dm id are invalid
def test_message_share_invalid_ids(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token3"],
        "og_message_id" : data["channel_message_id"],
        "message" : "",
        "channel_id":   -1234,
        "dm_id" : -1234
    })
    assert response.status_code == 400
    
def test_message_share_len_1005(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token2"],
        "og_message_id":    data["channel_message_id"],
        "message" :         "hello"*1005,
        "channel_id":       -1,
        "dm_id" :           data["dm_id"]
    })
    assert response.status_code == 400

# testing user in dm
def test_message_share_user_in_dm(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token1"],
        "og_message_id":    data["dm_message_id"],
        "message" :         "hello",
        "channel_id":       -1,
        "dm_id" :           data["dm_id"]
    })
    assert response.status_code == 200

# testing message in channel
def test_message_share_from_channel(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token2"],
        "og_message_id":    data["channel_message_id"],
        "message" :         "hello",
        "channel_id":       data["channel_id"],
        "dm_id" :           -1
    })
    assert response.status_code == 200

# testing user in dm
def test_message_share_user_msg_1001(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token1"],
        "og_message_id":    data["dm_message_id"],
        "message" :         "hello"*1001,
        "channel_id":       -1,
        "dm_id" :           data["dm_id"]
    })
    assert response.status_code == 400