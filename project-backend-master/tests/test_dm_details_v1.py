"""
Test the functionailty of channel detail.
"""
import pytest
import requests

from src.config import url
from src.error import AccessError, InputError
@pytest.fixture
def initialise():
    requests.delete(f"{url}/clear/v1")
    
    response_user_1 = requests.post(
        f"{url}auth/register/v2", json = {
            "email": "z5343970@gmail.com", 
            "password": "czt20020128", 
            "name_first": "Zhitao",
            "name_last": "Chen"
        })

    response_user_2 = requests.post(
        f"{url}auth/register/v2", json = {
            "email": "z536@unsw.edu.au", 
            "password": "Aa!F@32(Bc", 
            "name_first": "Tianyu",
            "name_last": "Wei"
        })

    response_user_3 = requests.post(
        f"{url}auth/register/v2", json = {
            "email": "z123@unsw.edu.au", 
            "password": "abcdefg", 
            "name_first": "Andrew",
            "name_last": "Wei"
        })

    resp_dm_1 = requests.post(
        f"{url}dm/create/v1", json = {
            "token": response_user_1.json()['token'],
            "u_ids": [],
        })

    return {
        "u_1_token": response_user_1.json()['token'],
        "u_2_token": response_user_2.json()['token'],
        "u_3_token": response_user_3.json()['token'],
        "dm_1_id": resp_dm_1.json()['dm_id'],
    }

def test_dm_details_valid(initialise):
    resp = requests.get(
        f"{url}dm/details/v1", params = {
            "token": initialise["u_1_token"],
            "dm_id": initialise["dm_1_id"]
        })

    assert resp.status_code == 200
    assert len(resp.json()['members']) == 1

def test_dm_details_invalid_token(initialise):
    resp = requests.get(
        f"{url}dm/details/v1", params = {
            "token": "u_invalid_token",
            "dm_id": initialise["dm_1_id"]
        })

    assert resp.status_code == AccessError.code

def test_dm_details_invalid_dm_id(initialise):
    resp = requests.get(
        f"{url}dm/details/v1", params = {
            "token": initialise["u_1_token"],
            "dm_id": -999999
        })

    assert resp.status_code == InputError.code

def test_dm_details_not_member(initialise):
    resp = requests.get(
        f"{url}dm/details/v1", params = {
            "token": initialise["u_3_token"],
            "dm_id": initialise["dm_1_id"]
        })

    assert resp.status_code == AccessError.code