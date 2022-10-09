import pytest
import requests
from src import config

@pytest.fixture
def get_an_email():
    requests.delete(config.url + 'clear/v1').json()

    email = "1531forgotpass@gmail.com"
    password = "abc123"
    first_name = "first"
    last_name = "last"
    re = requests.post(config.url + 'auth/register/v2', json={
        'email': email,
        'password': password,
        'name_first': first_name,
        'name_last': last_name
    })
    requests.post(config.url + 'auth/register/v2', json={
        'email': "tes123123@gmail.com",
        'password': "testingporpor",
        'name_first': "first_name11",
        'name_last': "last_name11"
    })
    return {"email":email, "token": re.json()['token']}

def test_successful_email(get_an_email):
    response = requests.post(config.url + '/auth/passwordreset/request/v1', json={
        'email': get_an_email["email"]
    })
    assert response.status_code == 200

def test_invalid_email():
    response = requests.post(config.url + '/auth/passwordreset/request/v1', json={
        'email': "Fakeemail93842@gmail.com"
    })
    assert response.status_code == 200

def test_successful_email_loggedout(get_an_email):
    resp_logout = requests.post(config.url + "auth/logout/v1", json = {
        "token": get_an_email["token"],
    })
    response = requests.post(config.url + '/auth/passwordreset/request/v1', json={
        'email': get_an_email['email']
    })
    
    assert response.status_code == 200
    assert resp_logout.status_code == 200