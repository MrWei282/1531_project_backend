'''testing for notifications get'''
import pytest
import requests

from src.config import url

@pytest.fixture
def initialise():
    requests.delete(f"{url}/clear/v1")

    response_user_1 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z5343970@gmail.com", 
             "password": "czt20020128", 
             "name_first": "Zhitao",
             "name_last": "Chen"
        })

    response_user_2 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z536@unsw.edu.au", 
             "password": "Aa!F@32(Bc", 
             "name_first": "Tianyu",
             "name_last": "Wei"
        })

    response_user_3 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z123@unsw.edu.au", 
             "password": "abcdefg", 
             "name_first": "Andrew",
             "name_last": "Wei"
        })

    resp_channel_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1.json()['token'],
            "name": "unsw discord server",
            "is_public": True
        })

    return {
        "u_1_token": response_user_1.json()['token'],
        "u_2_token": response_user_2.json()['token'],
        "u_3_token": response_user_3.json()['token'],
        "u_1_id": response_user_1.json()['auth_user_id'],
        "u_2_id": response_user_2.json()['auth_user_id'],
        "u_3_id": response_user_3.json()['auth_user_id'],
        "c_pub_1_id": resp_channel_1.json()['channel_id'],
    }

def test_channel_invite(initialise):
    resp_invite_1 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_2_id"]
        })
    assert resp_invite_1.status_code == 200
    
    resp_notifications_1 = requests.get(
        f"{url}/notifications/get/v1", params = {
            "token": initialise["u_2_token"]
        })
    assert resp_notifications_1.status_code == 200

def test_dm_create(initialise):
    resp_dm_create_1 = requests.post(
        f"{url}/dm/create/v1", json = {
            "token": initialise["u_1_token"],
            "u_ids": [initialise["u_2_id"], initialise["u_3_id"]]
        })
    assert resp_dm_create_1.status_code == 200
    
    resp_notifications_1 = requests.get(
        f"{url}/notifications/get/v1", params = {
            "token": initialise["u_2_token"]
        })
    assert resp_notifications_1.status_code == 200
    
    resp_notifications_2 = requests.get(
        f"{url}/notifications/get/v1", params = {
            "token": initialise["u_3_token"]
        })
    assert resp_notifications_2.status_code == 200

def test_msg_tag(initialise):
    resp_join_1 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_join_1.status_code == 200
    
    resp_msg_send_1 = requests.post(
        f"{url}/message/send/v1", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "message": "@tianyuwei okkkkk, just taging"
        })
    assert resp_msg_send_1.status_code == 200
    
    resp_notifications_1 = requests.get(
        f"{url}/notifications/get/v1", params = {
            "token": initialise["u_2_token"]
        })
    assert resp_notifications_1.status_code == 200

    resp_invite_1 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_3_id"]
        })
    assert resp_invite_1.status_code == 200

    resp_msg_send_1 = requests.post(
        f"{url}/message/send/v1", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "message": "@tianyuwei @andrewwei @zhitaochen okkkkk, just taging"
        })
    assert resp_msg_send_1.status_code == 200
    
    resp_notifications_1 = requests.get(
        f"{url}/notifications/get/v1", params = {
            "token": initialise["u_2_token"]
        })
    assert resp_notifications_1.status_code == 200

def test_msg_tag_dm(initialise):
    resp = requests.post(f"{url}/dm/create/v1", json={
        'token': initialise['u_1_token'],
        'u_ids': [initialise["u_2_id"], initialise["u_3_id"]],
    })
    assert resp.status_code == 200
    dm_id = resp.json()['dm_id']

    resp = requests.post(f"{url}/message/senddm/v1", json={
        'token': initialise['u_1_token'],
        'dm_id': dm_id,
        'message': '@tianyuwei @andrewwei @zhitaochen okkkkk, just taging but dm lol',
    })
    assert resp.status_code == 200
    
    resp_notifications_1 = requests.get(
        f"{url}/notifications/get/v1", params = {
            "token": initialise["u_1_token"]
        })
    assert resp_notifications_1.status_code == 200
