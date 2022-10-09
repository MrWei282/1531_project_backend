'''testfile for auth_user-login.py'''
import pytest
import requests

from src.config import url

@pytest.fixture
def initialise():
    requests.delete(f"{url}/clear/v1")

    response_user_1 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "czt@gmail.com", 
             "password": "czt0128", 
             "name_first": "zhitao",
             "name_last": "chen"
        })
    response_user_1_id = response_user_1.json()['auth_user_id']

    response_user_2 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z342@gmail.com", 
             "password": "shortttname", 
             "name_first": "Hi!",
             "name_last": "Great!Name"
        })
    response_user_2_id = response_user_2.json()['auth_user_id']

    response_user_3 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z420@gmail.com", 
             "password": "longgggname", 
             "name_first": "lwtwkadtcbkwakyviguaydiuvowbpavpaiv",
             "name_last": "cbaktwitkwjha"
        })
    response_user_3_id = response_user_3.json()['auth_user_id']
    
    return response_user_1_id, response_user_2_id, response_user_3_id

def test_successful_auth_login(initialise):
    '''testing for login with successful'''
    
    resp_1 = requests.post(
        f"{url}/auth/login/v2", json = {
            "email": "czt@gmail.com",
            "password": "czt0128"
        })
    assert resp_1.json()["auth_user_id"] == initialise[0]

    resp_2 = requests.post(
        f"{url}/auth/login/v2", json = {
            "email": "z342@gmail.com",
            "password": "shortttname"
        })
    assert resp_2.json()["auth_user_id"] == initialise[1]
    
    resp_3 = requests.post(
        f"{url}/auth/login/v2", json = {
            "email":"z420@gmail.com",
            "password":"longgggname"
        })
    assert resp_3.json()["auth_user_id"] == initialise[2]

def test_unregistered_email(initialise):
    '''Testing login with unregistered email'''
    
    resp_unregistered = requests.post(
        f"{url}/auth/login/v2", json = {
            "email": "z536@unsw.edu.au", 
            "password": "Aa!F@32(Bc"
        })
    assert resp_unregistered.status_code == 400
    
    resp_unregistered = requests.post(
        f"{url}/auth/login/v2", json = {
            "email": "random@gmail.com", 
            "password": "#@!cba321"
        })
    assert resp_unregistered.status_code == 400

def test_unregistered_auth_login(initialise):
    '''Testing login with wrong password'''

    resp_unregistered = requests.post(
        f"{url}/auth/login/v2", json = {
            "email": "czt@gmail.com", 
            "password": "wrong"
        })
    assert resp_unregistered.status_code == 400