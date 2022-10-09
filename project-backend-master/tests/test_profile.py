import pytest
import requests
from src.error import AccessError, InputError
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

    return {
        "u_1_token": response_user_1.json()['token'],
        "u_2_token": response_user_2.json()['token'],
        "u_1_id" : response_user_1.json()['auth_user_id'],
        "u_2_id" : response_user_2.json()['auth_user_id']
    }

def test_profile(initialise):
    ''' 
    Test the most basic usage of the function
    '''
    response = requests.get(url + "user/profile/v1" , params = {
            "token" : initialise["u_1_token"],
            "u_id" :  initialise["u_2_id"]
        })
    user_info = response.json()['user']
    assert response.status_code == 200
    assert user_info['name_first'] == "Tianyu"
    assert user_info['name_last'] == "Wei"
    assert user_info['u_id'] == initialise["u_2_id"]
    assert user_info['email'] == "z536@unsw.edu.au"

def test_invalid_id(initialise):
    ''' 
    Test when an invalid u_id is given
    '''
    response = requests.get(url + "user/profile/v1" , params = {
        "token" : initialise["u_1_token"],
        "u_id" : initialise["u_2_id"] + 400})

    assert response.status_code == InputError.code

def test_invalid_token(initialise):
    ''' 
    Test when an invalid token is given
    '''
    response = requests.get(url + "user/profile/v1" , params = {
        "token" : initialise["u_1_token"] + "invalid",
        "u_id" : initialise["u_2_id"]})
    assert response.status_code == AccessError.code

def test_removed_token(initialise):
    ''' 
    Test when an invalid token is given
    '''
    resp = requests.delete(url + 'admin/user/remove/v1', json={
        'token': initialise["u_1_token"],
        'u_id': initialise["u_2_id"],
    })
    assert resp.status_code == 200

    response = requests.get(url + "user/profile/v1" , params = {
        "token" : initialise["u_1_token"],
        "u_id" : initialise["u_2_id"]})
    assert response.status_code == 200

