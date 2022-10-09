
import requests
from src import config


def test_dm_remove():
    # clear
    assert requests.delete(config.url+'clear/v1').status_code == 200

    # register owner1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'one@mail.com',
        'password': 'abc123',
        'name_first': 'one',
        'name_last': 'one',
    })
    assert resp.status_code == 200
    owner1 = resp.json()

    # register member1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'two@mail.com',
        'password': 'abc123',
        'name_first': 'two',
        'name_last': 'two',
    })
    assert resp.status_code == 200
    member1 = resp.json()

    # create dm1
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': owner1['token'],
        'u_ids': [member1['auth_user_id']],
    })
    assert resp.status_code == 200
    dm = resp.json()

    # leave dm1
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': owner1['token'],
        'dm_id': dm['dm_id'],
    })
    assert resp.status_code == 200


def test_dm_remove_invalid_token():
    # clear
    assert requests.delete(config.url+'clear/v1').status_code == 200

    # register owner1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': '1@mail.com',
        'password': 'abc123',
        'name_first': 'one',
        'name_last': 'one',
    })
    assert resp.status_code == 200
    owner1 = resp.json()

    # register member1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': '2@gmail.com',
        'password': 'abc123',
        'name_first': 'two',
        'name_last': 'two',
    })
    assert resp.status_code == 200
    member1 = resp.json()

    # create dm1
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': owner1['token'],
        'u_ids': [member1['auth_user_id']],
    })
    assert resp.status_code == 200
    dm = resp.json()

    # leave dm1 with invalid token
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': 0,
        'dm_id': dm['dm_id'],
    })
    assert resp.status_code == 403

def test_dm_remove_nolonger_DM():
    # clear
    assert requests.delete(config.url+'clear/v1').status_code == 200

    # register owner1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'one@mail.com',
        'password': 'abc123',
        'name_first': 'one',
        'name_last': 'one',
    })
    assert resp.status_code == 200
    owner1 = resp.json()

    # register member1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'two@mail.com',
        'password': 'abc123',
        'name_first': 'two',
        'name_last': 'two',
    })
    assert resp.status_code == 200
    member1 = resp.json()

    # create dm1
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': owner1['token'],
        'u_ids': [member1['auth_user_id']],
    })
    assert resp.status_code == 200
    dm = resp.json()

    # leave dm1
    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': owner1['token'],
        'dm_id': dm['dm_id'],
    })
    assert resp.status_code == 200
    # leave dm1
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': owner1['token'],
        'dm_id': dm['dm_id'],
    })
    assert resp.status_code == 403
    
def test_dm_remove_notoriginalDM():
    # clear
    assert requests.delete(config.url+'clear/v1').status_code == 200

    # register owner1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'one@mail.com',
        'password': 'abc123',
        'name_first': 'one',
        'name_last': 'one',
    })
    assert resp.status_code == 200
    owner1 = resp.json()

    # register member1
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'two@mail.com',
        'password': 'abc123',
        'name_first': 'two',
        'name_last': 'two',
    })
    assert resp.status_code == 200
    member1 = resp.json()

    # create dm1
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': owner1['token'],
        'u_ids': [member1['auth_user_id']],
    })
    assert resp.status_code == 200
    dm = resp.json()

    # leave dm1
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': member1['token'],
        'dm_id': dm['dm_id'],
    })
    assert resp.status_code == 403
    
def test_dm_remove_reactDM():
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner = resp.json()

    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': owner['token'],
        'u_ids': [],
    })
    assert resp.status_code == 200
    dm_id = resp.json()['dm_id']

    resp = requests.post(config.url + 'message/senddm/v1', json={
        'token': owner['token'],
        'dm_id': dm_id,
        'message': 'hello',
    })
    assert resp.status_code == 200
    message_id1 = resp.json()['message_id']
    
    resp = requests.post(config.url + 'message/react/v1', json={
        'token': owner['token'],
        'message_id': message_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200