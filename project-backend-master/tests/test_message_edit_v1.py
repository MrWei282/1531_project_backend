import pytest
import requests
import json
from src import config
def test_message_edit():
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner = resp.json()

    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'Channel1',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'hello',
    })
    assert resp.status_code == 200
    message_id1 = resp.json()['message_id']

    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': owner['token'],
        'message_id': message_id1,
        'message': 'Good job',
    })
    assert resp.status_code == 200

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    messages = resp.json()['messages'][0]['message']
    assert resp.status_code == 200
    assert messages == "Good job"

def test_message_edit_invail_message():
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner = resp.json()
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'channel1',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'Hello World!',
    })
    assert resp.status_code == 200
    message_id1 = resp.json()['message_id']
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': owner['token'],
        'message_id': message_id1,
        'message': '',
    })
    assert resp.status_code == 200
    #test for more than 1000 char
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner = resp.json()
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'channel1',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'Hello!',
    })
    assert resp.status_code == 200
    message_id1 = resp.json()['message_id']
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': owner['token'],
        'message_id': message_id1,
        'message': 'hi'*1001,
    })
    assert resp.status_code == 400

def test_message_edit_input_error():
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200

    owner = resp.json()
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'Channel1',
        'is_public': True,
    })
    assert resp.status_code == 200

    channel_id = resp.json()['channel_id']
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'hello',
    })
    assert resp.status_code == 200

    message_id1 = resp.json()['message_id']
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': owner['token'],
        'message_id': message_id1,
        'message': 'Good job',
    })
    assert resp.status_code == 200

    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': owner['token'],
        'message_id': message_id1,
        'message': 'input',
    })
    assert resp.status_code == 200

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    messages = resp.json()['messages'][0]['message']
    assert resp.status_code == 200
    assert messages == "input"

def test_not_valid_msg_id():
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner = resp.json()

    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'Channel1',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'hello',
    })
    assert resp.status_code == 200
    message_id1 = resp.json()['message_id']

    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': owner['token'],
        'message_id': message_id1 + 10,
        'message': 'Good job',
    })
    assert resp.status_code == 400

def test_message_edit_dm():
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

    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': owner['token'],
        'message_id': message_id1,
        'message': 'Good job',
    })
    assert resp.status_code == 200

    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': owner['token'],
        'dm_id': dm_id,
        'start': 0,
    })
    messages = resp.json()['messages'][0]['message']
    assert resp.status_code == 200
    assert messages == "Good job"

def test_no_right_to_edit():
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner = resp.json()
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt123@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    user2 = resp.json()

    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'Channel1',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'hello',
    })
    assert resp.status_code == 200
    message_id1 = resp.json()['message_id']

    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': user2['token'],
        'message_id': message_id1,
        'message': 'Good job',
    })
    assert resp.status_code == 403
