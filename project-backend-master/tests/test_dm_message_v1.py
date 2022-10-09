import pytest
import requests
from src import config


@pytest.fixture
def token():
    requests.delete(config.url + 'clear/v1').json()

    email = "1@gamil.com"
    password = "abc123"
    first_name = "first"
    last_name = "first"
    auth_resp = requests.post(config.url + 'auth/register/v2', json={
        'email': email,
        'password': password,
        'name_first': first_name,
        'name_last': last_name
    })
    token = auth_resp.json()['token']
    return token


@pytest.fixture
def dm_id(token):
    member1 = requests.post(config.url + 'auth/register/v2', json={
        'email': "2@gamil.com",
        'password': "abc123",
        'name_first': "two",
        'name_last': "two"
    }).json()['auth_user_id']

    member2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "3@gamil.com",
        'password': "abc123",
        'name_first': "three",
        'name_last': "three"
    }).json()['auth_user_id']

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': token,
        'u_ids': [member1, member2]
    }).json()['dm_id']

    return dm_id


@pytest.fixture
def unauthorised_user():
    email = "4@gamil.com"
    password = "abc123"
    first_name = "four"
    last_name = "four"
    token = requests.post(config.url + 'auth/register/v2', json={
        'email': email,
        'password': password,
        'name_first': first_name,
        'name_last': last_name
    }).json()['token']
    return token


def test_invalid_token(dm_id):
    status_code = requests.get(config.url + 'dm/messages/v1', params={
        'token': "invalid_token",
        'dm_id': dm_id,
        'start': 0
    }).status_code

    assert status_code == 403


def test_invalid_dm_id(token, dm_id):
    status_code = requests.get(config.url + 'dm/messages/v1', params={
        'token': token,
        'dm_id': dm_id + 1,
        'start': 0
    }).status_code

    assert status_code == 400


def test_unauthorised_user(dm_id, unauthorised_user):
    status_code = requests.get(config.url + 'dm/messages/v1', params={
        'token': unauthorised_user,
        'dm_id': dm_id,
        'start': 0
    }).status_code

    assert status_code == 403


def test_invalid_start(token, dm_id):
    status_code = requests.get(config.url + 'dm/messages/v1', params={
        'token': token,
        'dm_id': dm_id,
        'start': 51
    }).status_code

    assert status_code == 400


def test_normal_message(token, dm_id):
    status_code = requests.get(config.url + 'dm/messages/v1', params={
        'token': token,
        'dm_id': dm_id,
        'start': 0
    }).status_code

    assert status_code == 200
