'''test file for channel listall'''
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
    }


def test_valid_email(initialise):
    ''' 
    Test the most basic usage of the function
    '''
    response = requests.put(url + "user/profile/setemail/v1" , json = {
        "token" : initialise["u_1_token"],
        "email" : "valid_email@gmail.com"})

    assert response.status_code == 200

def test_invalid_token_valid_email():
    ''' 
    Test invalid token 
    '''
    response = requests.put(url + "user/profile/setemail/v1" , json = {
        "token" : "invalid_token",
        "email" : "valid_email@gmail.com"})

    assert response.status_code == AccessError.code

def test_invalid_valid_email(initialise):
    ''' 
    Test invalid email
    '''
    response = requests.put(url + "user/profile/setemail/v1" , json = {
        "token" : initialise["u_1_token"],
        "email" : "invalid_email"})

    assert response.status_code == InputError.code

def test_email_used(initialise):
    ''' 
    Test used email
    '''
    response = requests.put(url + "user/profile/setemail/v1" , json = {
        "token" : initialise["u_1_token"],
        "email" : "z536@unsw.edu.au"})

    assert response.status_code == InputError.code
