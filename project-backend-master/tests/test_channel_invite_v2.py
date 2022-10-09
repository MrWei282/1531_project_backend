'''Import pytest for channel invite'''
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

def test_public_channel(initialise):
    '''testing for public channel'''

    resp_invite_1 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_2_id"]
        })
    assert resp_invite_1.status_code == 200

    resp_invite_2 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_3_id"],
            "u_id": initialise["u_3_id"]
        })
    assert resp_invite_2.status_code == 200
    
    resp_invite_3 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_3_id"]
        })
    assert resp_invite_3.status_code == 200

def test_private_channel(initialise):
    '''tesing private channel'''

    resp_invite_1 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pri_2_id"],
            "u_id": initialise["u_2_id"]
        })
    assert resp_invite_1.status_code == 200

    resp_invite_2 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pri_4_id"],
            "u_id": initialise["u_3_id"]
        })
    assert resp_invite_2.status_code == 200
    
    resp_invite_3 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pri_2_id"],
            "u_id": initialise["u_3_id"]
        })
    assert resp_invite_3.status_code == 200

def test_invalid_channel_id(initialise):
    '''testing invalid id for channel'''
    
    resp_join_invalid_cha = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": 999,
            "u_id": initialise["u_2_id"]
        })
    assert resp_join_invalid_cha.status_code == 400

def test_invalid_u_id(initialise):
    '''testing valid id of invitee id'''

    resp_join_invalid_uid = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": 999
        })
    assert resp_join_invalid_uid.status_code == 400

def test_user_already_in_channel(initialise):
    '''tesing whether user already in channel or not'''

    requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_2_id"]
        })
    
    resp_invite_2 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_2_id"]
        })
    assert resp_invite_2.status_code == 400
    
    resp_invite_3 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_1_id"]
        })
    assert resp_invite_3.status_code == 400

def test_no_access(initialise):
    '''invalid case when auth user is not already in channel and is not a global owner'''
    resp_invite_no_acc = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_3_id"]
        })
    assert resp_invite_no_acc.status_code == 403
    
    resp_invite_no_acc = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pri_2_id"],
            "u_id": initialise["u_3_id"]
        })
    assert resp_invite_no_acc.status_code == 403

def test_invalid_token(initialise):
    '''To check the raise error functionailty for invalid token.'''

    resp_join_invalid_tok_1 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": "invalid_token",
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_2_id"]
        })
    assert resp_join_invalid_tok_1.status_code == 403

    resp_join_invalid_tok_2 = requests.post(
        f"{url}/channel/invite/v2", json = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjF9.GUPqQ_DOSzE4aXkV7C8gnNCmf-V1ti5agmqq0moBtdw",
            "channel_id": initialise["c_pub_1_id"],
            "u_id": initialise["u_2_id"]
        })
    assert resp_join_invalid_tok_2.status_code == 403