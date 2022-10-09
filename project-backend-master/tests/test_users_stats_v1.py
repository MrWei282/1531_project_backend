from src.config import url
import requests
import pytest

@pytest.fixture
def data():
    requests.delete(url + 'clear/v1')
    response1 = requests.post(url + "auth/register/v2", json={
        "email": "czt@gmail.com",
        "password": "abc1234",
        "name_first": "zhitao",
        "name_last": "chen"
    })
    token1 = response1.json()["token"]

    response2 = requests.post(url + "auth/register/v2", json={
        "email": "czt2@gmail.com",
        "password": "abc1234",
        "name_first": "linbo",
        "name_last": "zhang"
    })
    token2 = response2.json()["token"]

    values = {
        "token1": token1,
        "token2": token2
    }
    return values

def test_initial_workspace_stats(data):
    token1 = data["token1"]
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == 200

def test_channels_create_workspace_stats(data):
    token1 = data["token1"]

    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == 200

def test_dm_create_workspace_stats(data):
    token1 = data["token1"]

    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": []
    })

    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == 200

def test_dm_remove_workspace_stats(data):
    token1 = data["token1"]

    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1]
    })

    requests.delete(url + "dm/remove/v1", json={
        "token": token1,
        "dm_id": 0
    })

    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == 200

def test_message_send_workspace_stats(data):
    token1 = data["token1"]

    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    requests.post(url + "message/send/v1", json={
        "token": token1,
        "channel_id": 0,
        "message": "okay"
    })

    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == 200

def test_message_senddm_workspace_stats(data):
    token1 = data["token1"]

    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": []
    })

    requests.post(url + "message/senddm/v1", json={
        "token": token1,
        "dm_id": 0,
        "message": "hello"
    })

    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == 200

def test_user_remove_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    requests.post(url + "channel/join/v2", json={
        "token": token2,
        "channel_id": 0,
    })

    requests.delete(url + "admin/user/remove/v1", json={
        "token": token1,
        "u_id": 1
    })

    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == 200
