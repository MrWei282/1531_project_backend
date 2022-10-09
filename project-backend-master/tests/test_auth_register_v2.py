'''test various cases for auth_register_v2'''
import pytest
import requests

from src.config import url

def test_normal_cases():
    '''Normal cases testing'''
    requests.delete(f"{url}/clear/v1")
    
    response_normal = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z536@unsw.edu.au", 
             "password": "Aa!F@32(Bc", 
             "name_first": "Tianyu",
             "name_last": "Wei"
        })
    assert response_normal.status_code == 200
    response_normal_data = response_normal.json()
    assert response_normal_data['auth_user_id'] == 1
    
    response_odd = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z342@gmail.com", 
             "password": "weirdname", 
             "name_first": "Hi",
             "name_last": "Great!Name"
        })
    assert response_odd.status_code == 200
    response_odd_data = response_odd.json()
    assert response_odd_data['auth_user_id'] == 2
    
    response_long = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z420@gmail.com", 
             "password": "longgggname", 
             "name_first": "FbXXlztXNNhwcWYraXlVYVyINFoIpEuOYnzmQcxcggYRYWMIe",
             "name_last": "cbaktwitkwjha"
        })
    assert response_long.status_code == 200
    response_long_data = response_long.json()
    assert response_long_data['auth_user_id'] == 3

def test_duplicate():
    '''testing whether registe duplicated'''
    requests.delete(f"{url}/clear/v1")

    response_1 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z123@unsw.edu.au", 
             "password": "abcdefg", 
             "name_first": "Andrew",
             "name_last": "Wei"
        })
    assert response_1.status_code == 200
    response_1_data = response_1.json()
    assert response_1_data['auth_user_id'] == 1

    response_2 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z456@unsw.edu.au", 
             "password": "hijklmn", 
             "name_first": "Andrew",
             "name_last": "Wei"
        })
    assert response_2.status_code == 200
    response_2_data = response_2.json()
    assert response_2_data['auth_user_id'] == 2

    response_3 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z789@unsw.edu.au", 
             "password": "asdhjk3", 
             "name_first": "Andrew",
             "name_last": "Wei"
        })
    assert response_3.status_code == 200
    response_3_data = response_3.json()
    assert response_3_data['auth_user_id'] == 3

def test_invalid_email_format():
    '''Testing login with invalid format in email'''
    # a valid syntax should follow this regular expression:
    # '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    requests.delete(f"{url}/clear/v1")
    password = "Pass123"
    name_first = "just"
    name_last = "name"
    
    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "*&^ v@&IAJH@A&*)c,.com", 
            "password": "invaliddd", 
            "name_first": "nothing",
            "name_last": "sus"
    })
    assert response.status_code == 400

    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "", 
            "password": "justtttt", 
            "name_first": "empty",
            "name_last": "email"
    })
    assert response.status_code == 400

    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "@google.com", 
            "password": password, 
            "name_first": name_first,
            "name_last": name_last
    })
    assert response.status_code == 400

    response = requests.post(
   f"{url}/auth/register/v2", json = {
            "email": "abcd@~`example.com", 
            "password": password, 
            "name_first": name_first,
            "name_last": name_last
    })
    assert response.status_code == 400

    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "ab@example.?c!?!m", 
            "password": password, 
            "name_first": name_first,
            "name_last": name_last
    })
    assert response.status_code == 400

def test_registered_email():
    '''testing whether register sucessfully'''
    requests.delete(f"{url}/clear/v1")

    response = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "George@google.edu.au", 
             "password": "heilongjiang", 
             "name_first": "hainan",
             "name_last": "Humohrey"
        })
    assert response.status_code == 200

    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "George@google.edu.au", 
            "password": "Aa!F@32(Bc", 
            "name_first": "Tianyu",
            "name_last": "Wei"
    })
    assert response.status_code == 400

def test_password_too_short():
    '''Testing invalid short passwords'''
    requests.delete(f"{url}/clear/v1")

    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "George@google.edu.au", 
            "password": "", 
            "name_first": "hainan",
            "name_last": "Humohrey"
    })
    assert response.status_code == 400

    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "valid@email.com", 
            "password": "12345", 
            "name_first": "jeremy",
            "name_last": "chung"
    })
    assert response.status_code == 400

def test_invalid_name_length():
    '''testing invalid name length'''
    requests.delete(f"{url}/clear/v1")

    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "regular@email.com", 
            "password": "alh2lhaw", 
            "name_first": "",
            "name_last": "onlylast"
    })
    assert response.status_code == 400
    
    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "George@google.edu.au", 
            "password": "adjlj1asjv", 
            "name_first": "onlyfirst",
            "name_last": ""    
    })
    assert response.status_code == 400
    
    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "z420@gmail.com", 
            "password": "longgggname", 
            "name_first": "FbXXlztXNNhwcWYraXlVYVyINFoIpEuOYnzmQcxAHCVLKAJLcggYRYWMIe",
            "name_last": "cbaktwitkwjha"    
    })
    assert response.status_code == 400
    
    response = requests.post(
    f"{url}/auth/register/v2", json = {
            "email": "valid@email.com", 
            "password": "longgggname", 
            "name_first": "cbaktwitkwjha",
            "name_last": "FbXXlztXNNhwcWYraXlVYVyINFoIpEuOYnzmQcxAHCVLKAJLcggYRYWMIe"    
    })
    assert response.status_code == 400
