"""
Test the functionailty of auth logout
"""
import pytest
import requests

from src.config import url
@pytest.fixture
def initialise():
    requests.delete(f"{url}clear/v1")

    response_user_1 = requests.post(
        f"{url}/auth/register/v2", json = {
            "email": "z5343970@gmail.com", 
            "password": "czt20020128", 
            "name_first": "Zhitao",
            "name_last": "Chen"
        })

    response_user_2 = requests.post(
        f"{url}/auth/register/v2", json = {
            "email": "random@gmail.com", 
            "password": "asdhla", 
            "name_first": "someone",
            "name_last": "random"
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
        "c_pub_1_id": resp_channel_1.json()['channel_id'],
    }

def test_logout(initialise):
    """"
    Test auth/logout and if the user token is still usuable after logout
    """
    resp_logout_1 = requests.post(
    f"{url}auth/logout/v1", json = {
        "token": initialise["u_1_token"],
    })
    resp_logout_1.status_code == 200

    resp_logout_2 = requests.post(
    f"{url}auth/logout/v1", json = {
        "token": initialise["u_2_token"],
    })
    resp_logout_2.status_code == 200

    resp_after_logout = requests.post(
        f"{url}/channel/join/v2", json = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"]
        })
    assert resp_after_logout.status_code == 403

def test_invalid_token(initialise):
    """
    Test for invalid token as input for auth_logoug_v1
    """
    logout = requests.post(
        f"{url}auth/logout/v1", json = {
            'token': 123,
        })
    assert logout.status_code == 403

    logout = requests.post(
        f"{url}auth/logout/v1", json = {
            'token': "invalid_token",
        })
    assert logout.status_code == 403