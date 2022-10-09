import pytest
import requests
import json
from src import config

@pytest.fixture
def set_up():
    '''
    Clears the server data and creates some users and channels.
    '''
    users = []
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'czt@gmail.com','password' : 'chen0128',
        'name_first' : 'Zhitao','name_last' : 'Chen'
    })
    users.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'czt1@gmail.com','password' : 'chen0128',
        'name_first' : 'Tianyu','name_last' : 'Chen'
    })
    users.append(json.loads(resp.text))
    return users

def test_invalid_token():
    resp = requests.get(config.url + 'users/all/v1', params={'token': ""})
    assert resp.status_code == 403

def test_valid_use(set_up):
    users = set_up
    resp = requests.get(config.url + 'users/all/v1', params={'token': users[0]['token']})
    assert resp.status_code == 200
    response_data = resp.json()
    print(f"\n{response_data}\n")
    assert response_data == {'users': [
        {'u_id': users[0]['auth_user_id'], 'email': 'czt@gmail.com', 'name_first': 'Zhitao',
         'name_last': 'Chen', 'handle_str': 'zhitaochen'},
        {'u_id': users[1]['auth_user_id'], 'email': 'czt1@gmail.com', 'name_first': 'Tianyu',
         'name_last': 'Chen', 'handle_str': 'tianyuchen'},
        ]}

