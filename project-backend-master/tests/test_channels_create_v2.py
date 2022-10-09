"""
Test the functionailty of channels_create.
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
    response_user_1_token = response_user_1.json()['token']
    
    response_user_2 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z536@unsw.edu.au", 
             "password": "Aa!F@32(Bc", 
             "name_first": "Tianyu",
             "name_last": "Wei"
        })
    response_user_2_token = response_user_2.json()['token']
    return response_user_1_token, response_user_2_token

def test_public_channel(initialise):
    """
    Assign two values to test the output of channel_id whether is correct.
    """
    user_1_token = initialise[0]
    user_2_token = initialise[1]
    
    resp_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_1_token,
            "name": "channel_7",
            "is_public": True
        })
    assert resp_1.status_code == 200
    resp_1_data = resp_1.json()
    assert resp_1_data['channel_id'] == 1
    
    resp_2 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_2_token,
            "name": "channel_9",
            "is_public": True
        })
    assert resp_2.status_code == 200
    resp_2_data = resp_2.json()
    assert resp_2_data['channel_id'] == 2

def test_same_channel_name(initialise):
    """
    Assign two values to test two outputs of channel_id whether the name is the same.
    """
    user_1_token = initialise[0]
    user_2_token = initialise[1]
    
    resp_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_1_token,
            "name": "channel_7",
            "is_public": True
        })
    assert resp_1.status_code == 200
    resp_1_data = resp_1.json()
    assert resp_1_data['channel_id'] == 1
    
    resp_2 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_2_token,
            "name": "channel_7",
            "is_public": True
        })
    assert resp_2.status_code == 200
    resp_2_data = resp_2.json()
    assert resp_2_data['channel_id'] == 2

def test_private_channel(initialise):
    """
    Assign two values to test private channel functionality is working as it design to be.
    """
    user_1_token = initialise[0]
    user_2_token = initialise[1]
    
    resp_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_1_token,
            "name": "channel_7",
            "is_public": False
        })
    assert resp_1.status_code == 200
    resp_1_data = resp_1.json()
    assert resp_1_data['channel_id'] == 1
    
    resp_2 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_2_token,
            "name": "channel_9",
            "is_public": False
        })
    assert resp_2.status_code == 200
    resp_2_data = resp_2.json()
    assert resp_2_data['channel_id'] == 2

def test_invalid_channel_name(initialise):
    user_1_token = initialise[0]
    user_2_token = initialise[1]
    
    resp_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_1_token,
            "name": "",
            "is_public": True
        })
    assert resp_1.status_code == 400
    
    resp_2 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": user_2_token,
            "name": "channel_longgggggggggggg",
            "is_public": False
        })
    assert resp_2.status_code == 400

def test_invalid_token(initialise):
    """
    To check the raise error functionailty for invalid token.
    """
    resp_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": "invalid_token",
            "name": "channel_7",
            "is_public": True
        })
    assert resp_1.status_code == 403

    resp_2 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjF9.GUPqQ_DOSzE4aXkV7C8gnNCmf-V1ti5agmqq0moBtdw",
            "name": "channel_9",
            "is_public": False
        })
    assert resp_2.status_code == 403
