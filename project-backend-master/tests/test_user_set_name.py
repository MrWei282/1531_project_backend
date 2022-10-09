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



def test_valid_name(initialise):
    ''' 
    Test the most basic usage of the function
    '''
    response = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : initialise["u_1_token"],
        "name_first" : "new_first",
        "name_last" : "new_last"})

    assert response.status_code == 200

def test_invalid_token_setname(initialise):
    '''
    Test when an invalid token is given
    '''
    response = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : 'invalidcewdvcvdevdsvrtf',
        "name_first" : "new_first",
        "name_last" : "new_last"})

    assert response.status_code == AccessError.code

def test_long_name(initialise):
    '''
    Test all the cases when the name is too long
    '''
    response = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : initialise["u_1_token"],
        "name_first" : "new_firstcwkdnvjersjkvnodslvnmeokvnerlvnjledfnv jekr",
        "name_last" : "new_last"})

    response2 = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : initialise["u_2_token"],
        "name_first" : "new_firstcwkdnvjersjkvnodslvnmeokvnerlvnjledfnv jekr",
        "name_last" : "new_last"})

    assert response.status_code == InputError.code
    assert response2.status_code == InputError.code

    response = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : initialise["u_1_token"],
        "name_first" : "new_first",
        "name_last" : "new_lastcwkdnvjersjkvnodslvnmeokvnerlvnjledfnv jekr"})

    response2 = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : initialise["u_2_token"],
        "name_first" : "new_first",
        "name_last" : "new_lastcwkdnvjersjkvnodslvnmeokvnerlvnjledfnv jekr"})

    assert response.status_code == InputError.code
    assert response2.status_code == InputError.code

def test_short_name(initialise):
    '''
    Test all the cases when the name is too short
    '''
    response = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : initialise["u_1_token"],
        "name_first" : "",
        "name_last" : "new_last"})

    response2 = requests.put(url + "user/profile/setname/v1" , json = {
        "token" : initialise["u_2_token"],
        "name_first" : "new_first",
        "name_last" : ""})

    assert response.status_code == InputError.code
    assert response2.status_code == InputError.code