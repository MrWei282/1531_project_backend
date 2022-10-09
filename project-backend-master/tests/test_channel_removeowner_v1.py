import pytest
import requests
import json
from src import config
def test_http_channel_addowner_removeowner():
    '''
    http test for channel_removeowner nice work
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
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 200
    #res = requests.get(config.url + 'channel/details/v2', json={
    #    'token': owner['token'],
    #    'channel_id': channel['channel_id'],
    #})
    #assert res.status_code == 200
    #details = res.json()
    #assert len(details['owner_members']) == 2

    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 200

    #res = requests.get(config.url + 'channel/details/v2', json={
    #    'token': owner['token'],
    #    'channel_id': channel['channel_id'],
    #})
    #assert res.status_code == 200
    #details = res.json()
    #assert len(details['owner_members']) == 1

def test_http_channel_removeowner_user_no_permission():
    '''
    channel_id is valid and the authorised user does not have owner permissions in the channel
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
    #assert res.status_code == 200
    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner['auth_user_id']
    })
    assert res.status_code == 400
def test_http_channel_addowner_removeowner_invalid_channel_id():
    '''
    channel_id does not refer to a valid channel
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
    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id']+100,
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 400
def test_http_channel_removeowner_user_not_in_channel():
    '''
    u_id refers to a user who is not an owner of the channel
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

    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 400

def test_http_channel_removeowner_only_owner():
    '''
    u_id refers to a user who is currently the only owner of the channel
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
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

    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner['auth_user_id']
    })
    assert res.status_code == 400

def test_removeowner_not_owner_of_the_channel():
    '''
    testing u_id refers to a user who is not an owner of the channel
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

    res = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com',
        'password' : 'czt0128',
        'name_first' : 'tianyu',
        'name_last' : 'chen'
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
    
    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
        'u_id': owner['auth_user_id']
    })
    assert res.status_code == 400

    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 403

    res = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'u_id': member['auth_user_id']
    })
    assert res.status_code == 400