'''testing for channel leave'''

import requests
from src import config
def test_channel_leave():
    '''
    Tests to see if channel_leave_v1() is working as intended
    '''
    resp = requests.delete(config.url + 'clear/v1')

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com',
        'password' : 'czt0128',
        'name_first' : 'zhitao',
        'name_last' : 'chen'
    })
    register_1 = resp.json()
    
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com',
        'password' : 'czt0128',
        'name_first' : 'tianyu',
        'name_last' : 'chen'
    })
    register_2 = resp.json()
    
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt2@gmail.com',
        'password' : 'czt0128',
        'name_first' : 'linbo',
        'name_last' : 'chen'
    })
    register_3 = resp.json()
    
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token':register_1['token'],
        'name':'channel1',
        'is_public':True})
    new_channel = resp.json()
    
    requests.post(config.url + 'channel/invite/v2', json={
        'token': register_1['token'],
        'channel_id': new_channel['channel_id'],
        'u_id':register_2['auth_user_id']})
    
    test_1 = requests.post(config.url + 'channel/leave/v1', json={
        'token': register_2['token'],
        'channel_id': new_channel['channel_id']})
    assert test_1.status_code == 200

    test_2 = requests.post(config.url + 'channel/leave/v1', json={
        'token': register_1['token'],
        'channel_id': new_channel['channel_id'] + 1})
    assert test_2.status_code == 400

    test_3 = requests.post(config.url + 'channel/leave/v1', json={
        'token': register_3['token'],
        'channel_id': new_channel['channel_id']})
    assert test_3.status_code == 403

    test_4 = requests.post(config.url + 'channel/leave/v1', json={
        'token': register_1['token'],
        'channel_id': new_channel['channel_id']})
    assert test_4.status_code == 200

