import pytest
import requests

from src.config import url
from src.error import InputError

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
    return {
        "u_1_token": response_user_1.json()['token'],
        "u_2_token": response_user_2.json()['token'],
    }
    
def test_random_code(initialise):
    response = requests.post(
        f"{url}/auth/passwordreset/reset/v1", json = {
            "reset_code": "eiasfncwfwnecinweic", 
            "new_password": "czt20020128", 
    })
    assert response.status_code == InputError.code

def test_incorrect_pass(initialise):
    response = requests.post(
        f"{url}/auth/passwordreset/reset/v1", json = {
            "reset_code": "eiasfncwfwnecinweic", 
            "new_password": "", 
    })
    assert response.status_code == InputError.code
