import requests
from src import config

def test_admin_user_remove():
    '''
    normal case for user remove
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner =    resp.json()

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert resp.status_code == 200
    member =   resp.json()

    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': owner['token'],
        'name': 'Channel1',
        'is_public': True,
    })
    resp2 = requests.post(config.url + 'channels/create/v2', json={
        'token': member['token'],
        'name': 'Channel2',
        'is_public': True,
    })
    assert resp2.status_code == 200
    assert resp.status_code == 200
    channel =  resp.json()

    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
    })
    assert resp.status_code == 200

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': member['token'],
        'channel_id': channel['channel_id'],
        'message': 'hello',
    })
    assert resp.status_code == 200
    resp2 = requests.post(config.url + 'message/send/v1', json={
        'token': owner['token'],
        'channel_id': channel['channel_id'],
        'message': 'hell rthhrthrto',
    })
    assert resp2.status_code == 200

    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': owner['token'],
        'u_id': member['auth_user_id'],
    })
    assert resp.status_code == 200

def test_admin_user_remove_only_owner():
    '''
    u_id refers to a user who is the only global owner
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner =    resp.json()

    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': owner['token'],
        'u_id': owner['auth_user_id'],
    })
    assert resp.status_code == 400

def test_admin_user_remove_not_owner():
    '''
    the authorised user is not a global owner
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner =    resp.json()

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    assert resp.status_code == 200
    member =   resp.json()

    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': member['token'],
        'u_id': owner['auth_user_id'],
    })
    assert resp.status_code == 403

def test_admin_user_remove_invalid_uid():
    '''
    u_id does not refer to a valid user
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner =    resp.json()
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': owner['token'],
        'u_id': 9,
    })
    assert resp.status_code == 400

def test_admin_user_remove_from_dm():
    '''
    normal case for user remove
    '''
    assert requests.delete(config.url + 'clear/v1').status_code == 200

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    assert resp.status_code == 200
    owner =    resp.json()

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'
    })
    resp8 = requests.post(config.url + 'auth/register/v2', json={
        'email' : 'czt2@gmail.com','password' : 'czt0128',
        'name_first' : 'daishi','name_last' : 'chkken'
    })
    member2 =   resp.json()
    assert resp8.status_code == 200
    assert resp.status_code == 200
    member =   resp.json()

    requests.post(config.url + "dm/create/v1", json={
        "token": owner['token'],
        "u_ids": [member['auth_user_id'],member2['auth_user_id']]
    })

    requests.post(config.url + "dm/create/v1", json={
        "token": member['token'],
        "u_ids": []
    })
    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': owner['token'],
        'u_id': member['auth_user_id'],
    })
    assert resp.status_code == 200