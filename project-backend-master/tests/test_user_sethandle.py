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

def test_set_normal_handle(initialise):
    ''' 
    Test the most basic usage of the function
    '''
    response = requests.put(url + "user/profile/sethandle/v1" , json = {
        "token" : initialise["u_1_token"],
        "handle_str" : "validhandle"})

    check_handle = requests.get(url + "user/profile/v1" , params = {
            "token" : initialise["u_1_token"],
            "u_id" :  initialise["u_1_id"]
        })

    assert response.status_code == 200
    assert check_handle.json()['user']['handle_str'] == "validhandle"

def test_already_used(initialise):
    ''' 
    Test try to change the handle into an already used handle_str
    '''
    response = requests.put(url + "user/profile/sethandle/v1" , json = {
        "token" : initialise["u_1_token"],
        "handle_str" : "validhandle"})
    
    response2 = requests.put(url + "user/profile/sethandle/v1" , json = {
        "token" : initialise["u_2_token"],
        "handle_str" : "validhandle"})

    assert response.status_code == 200
    assert response2.status_code == InputError.code

def test_invalid_lenght(initialise):
    ''' 
    Try to change the handle into a handle either too long or too short
    '''
    response = requests.put(url + "user/profile/sethandle/v1" , json = {
        "token" : initialise["u_1_token"],
        "handle_str" : "f"})

    assert response.status_code == InputError.code

    response2 = requests.put(url + "user/profile/sethandle/v1" , json = {
        "token" : initialise["u_1_token"],
        "handle_str" : "Thishanldeisnotvalidbecauseistoooooolonnggggwoc"})

    assert response2.status_code == InputError.code

def test_invalid_token(initialise):
    ''' 
    Use an invalid token
    '''
    response = requests.put(url + "user/profile/sethandle/v1" , json = {
        "token" : initialise["u_1_token"] + "invalid",
        "handle_str" : "f"})

    assert response.status_code == AccessError.code

def test_hanlde_not_alphanumeric(initialise):
    '''
    Try to set a handle which is not alphanumeric
    '''
    response = requests.put(url + "user/profile/sethandle/v1" , json = {
        "token" : initialise["u_1_token"],
        "handle_str" : "inva*&^%$#@#%$^$q"})

    assert response.status_code == InputError.code

