'''
dm_create_v1_test
'''

import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates 3 users for dm_create_setup
    '''
    requests.delete(config.url + 'clear/v1')
    user1 = requests.post(config.url + f"auth/register/v2", json={
        'email': '1@mail.com',
        'password': 'abc123',
        'name_first': 'one',
        'name_last': 'one'
    })
    creator = json.loads(user1.text)

    user2 = requests.post(config.url + f"auth/register/v2", json={
        'email': '2@mail.com',
        'password': 'abc123',
        'name_first': 'two',
        'name_last': 'two'
    })
    member1 = json.loads(user2.text)
    u_ids = [member1['auth_user_id']]

    user3 = requests.post(config.url + f"auth/register/v2", json={
        'email': '3@mail.com',
        'password': 'abc123',
        'name_first': 'three',
        'name_last': 'three'
    })
    member2 = json.loads(user3.text)
    u_ids.append(member2['auth_user_id'])

    return (creator, u_ids)


def test_dms_valid_create(setup):
    '''
    A simple test to check a valid dm creation
    '''
    creator, u_ids = setup
    dm = requests.post(config.url + 'dm/create/v1',
                       json={'token': creator['token'], 'u_ids': u_ids})
    assert dm.status_code == 200


def test_invalid_token(setup):
    '''
#    A simple test to check a invalid dm creation for invaid token pass in
#    '''
    u_ids = setup[1]
    dm = requests.post(config.url + 'dm/create/v1',
                       json={'token': '', 'u_ids': u_ids})
    assert dm.status_code == 403


def test_invalid_uids(setup):
    '''
    A simple test to check a invalid dm creation for invaid uids(unregisted user) pass in
    '''
    creator = setup[0]
    dm = requests.post(config.url + 'dm/create/v1',
                       json={'token': creator['token'], 'u_ids': [3, 4]})
    assert dm.status_code == 400
