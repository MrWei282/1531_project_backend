import pytest
import requests
from time import sleep
from src import config
import datetime


BASE_URL = config.url


@pytest.fixture(autouse=True)
def clear():
    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(config.url + "clear/v1")
    assert response.status_code == 200
    assert response.json() == {}


def register_user(email, password, name_first, name_last):
    '''
    Registers a new user with given parameters and returns the users token
    '''

    response = requests.post(config.url + "auth/register/v2", json={
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    })

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data['token'], str)
    assert isinstance(response_data['auth_user_id'], int)
    return response_data


def dm_create_endpoint(token, u_ids):
    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        'token': token,
        'u_ids': u_ids,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data


def sendlaterdm(token, dm_id, message, time_sent):
    '''
    Sends msg after x time
    '''

    response = requests.post(config.url + "message/sendlaterdm/v1", json={
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data


def dm_messages_endpoint(token, dm_id, start):
    '''
    Calling dm messages to list the most recent 50 messages in dm from start index
    '''
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        'token': token,
        'dm_id': dm_id,
        'start': start
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data


@pytest.fixture
def setup():
    users = []
    users.append(register_user(
        'a@email.com', 'Pass123456', 'tianyu', 'wang'))
    users.append(register_user(
        'b@email.com', 'Pass123456', 'zhitao', 'zhou'))
    users.append(register_user(
        'c@email.com', 'Pass123456', 'qinghuan', 'zhong'))
    dm = dm_create_endpoint(users[0]['token'], [users[1]['auth_user_id']])
    return (users, dm)


def test_invalid_dm_id(setup):
    users, dm = setup
    response = requests.post(config.url + "message/sendlaterdm/v1", json={
        'token': users[0]['token'],
        'dm_id': dm['dm_id'] + 1,
        'message': "Hello",
        'time_sent': int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp())
    })
    assert response.status_code == 400


def test_invalid_dm_length(setup):
    users, dm = setup
    thousand_string = ''
    for i in range(1005):
        thousand_string += str(i)
    response = requests.post(config.url + "message/sendlaterdm/v1", json={
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'message': thousand_string,
        'time_sent': int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp())
    })
    assert response.status_code == 400


def test_invalid_time(setup):
    users, dm = setup
    response = requests.post(config.url + "message/sendlaterdm/v1", json={
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'message': "Hello",
        'time_sent': int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()) - 1
    })
    assert response.status_code == 400


def test_valid_dm_user_nonmember(setup):
    users, dm = setup
    response = requests.post(config.url + "message/sendlaterdm/v1", json={
        'token': users[2]['token'],
        'dm_id': dm['dm_id'],
        'message': "Hello",
        'time_sent': int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp())
    })
    assert response.status_code == 403


def test_valid_sendlater(setup):
    users, dm = setup
    sendlaterdm(users[0]['token'], dm['dm_id'], "Hello", int(
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()) + 5)
    sleep(5)
    messages = dm_messages_endpoint(
        users[0]['token'], dm['dm_id'], 0)['messages']
    for message in messages:
        assert message['message'] == "Hello"


def test_valid_sendlater_user_handle(setup):
    users, dm = setup
    sendlaterdm(users[0]['token'], dm['dm_id'], "@tianyuwang, Hello", int(
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()) + 5)
    sleep(5)
    messages = dm_messages_endpoint(
        users[0]['token'], dm['dm_id'], 0)['messages']
    for message in messages:
        assert message['message'] == "@tianyuwang, Hello"

def test_valid_dm_10001_chars(setup):
    users, dm = setup
    response = requests.post(config.url + "message/sendlaterdm/v1", json={
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'message': "Hello"*1001,
        'time_sent': int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp())
    })
    assert response.status_code == 400