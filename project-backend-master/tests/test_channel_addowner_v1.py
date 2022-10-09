import pytest
import requests
import json
from src import config
def test_http_channel_addowner():
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert res.status_code == 200
    owner = res.json()

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert res.status_code == 200
    member = res.json()

    res = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'channel1',
        'is_public': True,
    })
    assert res.status_code == 200
    channel = res.json()

    res = requests.post(config.url + 'channel/join/v2', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
    })
    assert res.status_code == 200

    res = requests.post(config.url + 'channel/addowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 200
    

def test_http_channel_addowner_invalid_channel_id():
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert res.status_code == 200
    owner = res.json()

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert res.status_code == 200
    member = res.json()

    res = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'channel1',
        'is_public': True,
    })
    assert res.status_code == 200
    channel = res.json()

    res = requests.post(config.url + 'channel/join/v2', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
    })
    assert res.status_code == 200

    res = requests.post(config.url + 'channel/addowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id']+100,
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 400

def test_http_channel_addowner_already_owner():
    '''
    http test for channel_addowner for where user is already owner
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com',
        'password' : 'czt0128',
        'name_first' : 'zhitao',
        'name_last' : 'chen'
    })
    assert res.status_code == 200
    owner = res.json()

    res = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'channel1',
        'is_public': True,
    })
    assert res.status_code == 200
    channel = res.json()

    res = requests.post(config.url + 'channel/addowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner['auth_user_id']
    })
    assert res.status_code == 400

def test_http_channel_addowner_user_not_in_channel():
    '''
    http test for channel_addowner for user not in channel
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert res.status_code == 200
    owner = res.json()
    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert res.status_code == 200
    member = res.json()

    res = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'channel1',
        'is_public': True,
    })
    assert res.status_code == 200
    channel = res.json()

    res = requests.post(config.url + 'channel/addowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 400
def test_http_channel_addowner_user_no_permission():
    '''
    http test for channel_addowner for user has no permission
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert res.status_code == 200
    owner = res.json()

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert res.status_code == 200
    member = res.json()

    res = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'channel1',
        'is_public': True,
    })
    assert res.status_code == 200
    channel = res.json()

    res = requests.post(config.url + 'channel/join/v2', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
    })
    assert res.status_code == 200

    res = requests.post(config.url + 'channel/addowner/v1', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 403
