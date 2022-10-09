"""
Test the functionailty of channel detail.
"""
import pytest
import requests

from src.config import url
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

    resp_channel_1 = requests.post(
        f"{url}channels/create/v2", json = {
            "token": response_user_1.json()['token'],
            "name": "unsw discord server",
            "is_public": True
        })

    return {
        "u_1_token": response_user_1.json()['token'],
        "u_2_token": response_user_2.json()['token'],
        "u_3_token": response_user_3.json()['token'],
        "c_pub_1_id": resp_channel_1.json()['channel_id'],
    }


def test_channel_details_single_member(initialise):
    """
    Test the functionailty of return value of channel detail with single member as input.
    """

    resp_detail_single = requests.get(
        f"{url}channel/details/v2", params = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_detail_single.status_code == 200

    assert resp_detail_single.json()["name"] == 'unsw discord server'
    assert resp_detail_single.json()["is_public"] == True
    assert resp_detail_single.json()["owner_members"] == [{
                                                        'u_id': 1,
                                                        'email': 'z5343970@gmail.com',
                                                        'name_first': 'Zhitao',
                                                        'name_last': 'Chen',
                                                        'handle_str': 'zhitaochen',
                                                        }]
    assert resp_detail_single.json()["all_members"] == [{
                                                        'u_id': 1,
                                                        'email': 'z5343970@gmail.com',
                                                        'name_first': 'Zhitao',
                                                        'name_last': 'Chen',
                                                        'handle_str': 'zhitaochen',
                                                        }]

def test_channel_details_multiple_members(initialise):
    """
    Test the functionailty of return value of channel detail with multiple member as input.
    """

    requests.post(
        f"{url}channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    
    requests.post(
        f"{url}channel/join/v2", json = {
            "token": initialise["u_3_token"],
            "channel_id": initialise["c_pub_1_id"]
        })

    resp_detail_multi = requests.get(
        f"{url}channel/details/v2", params = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_detail_multi.status_code == 200

    assert len(resp_detail_multi.json()["owner_members"]) == 1
    assert len(resp_detail_multi.json()["all_members"]) == 3
    
def test_channel_details_invalid_channel_id(initialise):
    """
    Test the functionailty of return value of channel detail with error input.
    """
    resp_detail_invalid_cha = requests.get(
        f"{url}channel/details/v2", params = {
            "token": initialise["u_1_token"],
            "channel_id": 999
        })
    assert resp_detail_invalid_cha.status_code == 400

def test_channel_details_auth_user_not_a_member(initialise):
    """
    Test the functionailty of return value of channel detail with error input.
    """

    resp_detail_not_member = requests.get(
        f"{url}channel/details/v2", params = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_detail_not_member.status_code == 403

def test_invalid_token(initialise):
    """
    To check the raise error functionailty for invalid token.
    """

    resp_detail_invalid_tok_1 = requests.get(
        f"{url}channel/details/v2", params = {
            "token": "invalid_token",
            "channel_id": initialise["c_pub_1_id"],
        })
    assert resp_detail_invalid_tok_1.status_code == 403

    resp_detail_invalid_tok_2 = requests.get(
        f"{url}channel/details/v2", params = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjF9.GUPqQ_DOSzE4aXkV7C8gnNCmf-V1ti5agmqq0moBtdw",
            "channel_id": initialise["c_pub_1_id"],
        })
    assert resp_detail_invalid_tok_2.status_code == 403

