'''testing for channel joining'''
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
    response_user_1_token = response_user_1.json()['token']

    response_user_2 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z536@unsw.edu.au", 
             "password": "Aa!F@32(Bc", 
             "name_first": "Tianyu",
             "name_last": "Wei"
        })
    response_user_2_token = response_user_2.json()['token']

    response_user_3 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z123@unsw.edu.au", 
             "password": "abcdefg", 
             "name_first": "Andrew",
             "name_last": "Wei"
        })
    response_user_3_token = response_user_3.json()['token']

    resp_channel_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1_token,
            "name": "unsw discord server",
            "is_public": True
        })
    resp_channel_1_id = resp_channel_1.json()['channel_id']

    resp_channel_2 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1_token,
            "name": "private chat room",
            "is_public": False
        })
    resp_channel_2_id = resp_channel_2.json()['channel_id']

    resp_channel_3 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1_token,
            "name": "random server",
            "is_public": True
        })
    resp_channel_3_id = resp_channel_3.json()['channel_id']

    resp_channel_4 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1_token,
            "name": "selective club",
            "is_public": False
        })
    resp_channel_4_id = resp_channel_4.json()['channel_id']

    return {
        "u_1_token": response_user_1_token,
        "u_2_token": response_user_2_token,
        "u_3_token": response_user_3_token,
        "c_pub_1_id": resp_channel_1_id,
        "c_pri_2_id": resp_channel_2_id,
        "c_pub_3_id": resp_channel_3_id,
        "c_pri_4_id": resp_channel_4_id,
    }

def test_public_channel(initialise):
    '''testing for joining public channel'''

    resp_join_1 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_join_1.status_code == 200

    resp_join_2 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_3_token"],
            "channel_id": initialise["c_pub_3_id"]
        })
    assert resp_join_2.status_code == 200

def test_invalid_channel_id(initialise):
    '''testing for join invalid channel'''

    resp_join_invalid_cha_1 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": 0
        })
    assert resp_join_invalid_cha_1.status_code == 400

    resp_join_invalid_cha_2 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_3_token"],
            "channel_id": 999
        })
    assert resp_join_invalid_cha_2.status_code == 400

def test_user_already_in_channel(initialise):
    '''testing whether auth user already in the channel'''

    resp_join_already_1 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_join_already_1.status_code == 400
    
    resp_join_already_2 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pri_2_id"]
        })
    assert resp_join_already_2.status_code == 400

def test_private_no_access(initialise):
    '''testing whether have the right to access private channel'''
    
    resp_join_no_acc_1 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pri_2_id"]
        })
    assert resp_join_no_acc_1.status_code == 403

    resp_join_no_acc_2 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pri_4_id"]
        })
    assert resp_join_no_acc_2.status_code == 403

def test_invalid_token(initialise):
    '''To check the raise error functionailty for invalid token.'''

    resp_join_invalid_tok_1 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": "invalid_token",
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_join_invalid_tok_1.status_code == 403
    
    resp_join_invalid_tok_2 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjF9.GUPqQ_DOSzE4aXkV7C8gnNCmf-V1ti5agmqq0moBtdw",
            "channel_id": initialise["c_pri_2_id"]
        })
    assert resp_join_invalid_tok_2.status_code == 403

    resp_join_invalid_tok_3 = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjk5OSwic2Vzc2lvbl9pZCI6LTk5OX0.LEy25lpERCOKCqx2HZfc84ccxDthAcfYd_GExO2wELA",
            "channel_id": initialise["c_pri_2_id"]
        })
    assert resp_join_invalid_tok_3.status_code == 403
