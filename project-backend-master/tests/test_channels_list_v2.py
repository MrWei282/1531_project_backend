"""
test for channel_list_v1
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

    resp_channel_3 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1.json()['token'],
            "name": "random server",
            "is_public": True
        })

    resp_channel_4 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1.json()['token'],
            "name": "selective club",
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
        "c_pub_3_id": resp_channel_3.json()['channel_id'],
        "c_pri_4_id": resp_channel_4.json()['channel_id'],
    }

def test_channel(initialise):
    """
    test for channel listing
    """

    resp_list_1 = requests.get(
        f"{url}/channels/list/v2", params = {
            "token": initialise["u_1_token"]
        })
    assert resp_list_1.status_code == 200
    assert resp_list_1.json()["channels"] == [{"channel_id": 1, "name": "unsw discord server"}, 
                                              {"channel_id": 2, "name": "private chat room"},
                                              {"channel_id": 3, "name": "random server"},
                                              {"channel_id": 4, "name": "selective club"},]
    
    requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"]
        })

    requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_3_id"]
        })

    resp_list_2 = requests.get(
        f"{url}/channels/list/v2", params = {
            "token": initialise["u_2_token"]
        })
    assert resp_list_2.status_code == 200
    assert resp_list_2.json()["channels"] == [{"channel_id": 1, "name": "unsw discord server"}, 
                                              {"channel_id": 3, "name": "random server"},]

    requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pri_2_id"],
            "u_id": initialise["u_3_id"]
        })

    requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pri_4_id"],
            "u_id": initialise["u_3_id"]
        })
    
    resp_list_3 = requests.get(
        f"{url}/channels/list/v2", params = {
            "token": initialise["u_3_token"]
        })
    assert resp_list_3.status_code == 200
    assert resp_list_3.json()["channels"] == [{"channel_id": 2, "name": "private chat room"}, 
                                              {"channel_id": 4, "name": "selective club"},]
    
def test_invalid_token(initialise):
    '''To check the raise error functionailty for invalid token.'''

    resp_list_1 = requests.get(
        f"{url}/channels/list/v2", params = {
            "token": "invalid_token"
        })
    assert resp_list_1.status_code == 403

    resp_list_2 = requests.get(
        f"{url}/channels/list/v2", params = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjF9.GUPqQ_DOSzE4aXkV7C8gnNCmf-V1ti5agmqq0moBtdw"
        })
    assert resp_list_2.status_code == 403
