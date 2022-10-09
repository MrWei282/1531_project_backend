"""
test for the standup start
"""
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

    resp_channel_2 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1.json()['token'],
            "name": "private chat room",
            "is_public": False
        })

    return {
        "u_1_token": response_user_1.json()['token'],
        "u_2_token": response_user_2.json()['token'],
        "u_3_token": response_user_3.json()['token'],
        "u_1_id": response_user_1.json()['auth_user_id'],
        "u_2_id": response_user_2.json()['auth_user_id'],
        "u_3_id": response_user_3.json()['auth_user_id'],
        "c_pub_1_id": resp_channel_1.json()['channel_id'],
        "c_pri_2_id": resp_channel_2.json()['channel_id'],
    }

def test_standup_start_normal(initialise):
    resp_standup_start_1 = requests.post(
        f"{url}/standup/start/v1", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "length": 10
        })
    resp_standup_start_1.status_code == 200

    resp_standup_active_1 = requests.get(
        f"{url}/standup/active/v1", params = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_standup_active_1.status_code == 200
    assert resp_standup_active_1.json()["is_active"] == True

def test_standup_start_multiple(initialise):
    resp_join_1 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_join_1.status_code == 200
    
    resp_standup_start_1 = requests.post(
        f"{url}/standup/start/v1", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "length": 20
        })
    resp_standup_start_1.status_code == 200

    resp_standup_active_1 = requests.get(
        f"{url}/standup/active/v1", params = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_standup_active_1.status_code == 200
    assert resp_standup_active_1.json()["is_active"] == True
    
    resp_standup_start_2 = requests.post(
        f"{url}/standup/start/v1", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "length": 10
        })
    assert resp_standup_start_2.status_code == 400

def test_standup_start_invalid_ch(initialise):
    resp_standup_start_1 = requests.post(
        f"{url}/standup/start/v1", json = {
            "token": initialise["u_1_token"],
            "channel_id": -999,
            "length": 20
        })
    assert resp_standup_start_1.status_code == 400
    
def test_standup_start_invalid_length(initialise):
    resp_standup_start_1 = requests.post(
        f"{url}/standup/start/v1", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "length": -999
        })
    assert resp_standup_start_1.status_code == 400

def test_standup_start_not_member(initialise):
    resp_standup_start_1 = requests.post(
        f"{url}/standup/start/v1", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pri_2_id"],
            "length": 10
        })
    assert resp_standup_start_1.status_code == 403