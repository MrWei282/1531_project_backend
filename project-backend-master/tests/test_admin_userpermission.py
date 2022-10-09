import pytest
import requests
from src.config import url

@pytest.fixture
def data():
    requests.delete(url + 'clear/v1')

    response1 = requests.post(url + "auth/register/v2", json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'

    })
    token1 = response1.json()["token"]
    response2 = requests.post(url + "auth/register/v2", json={
        'email' : 'czt1@gmail.com','password' : 'czt0128',
        'name_first' : 'tianyu','name_last' : 'chen'

    })
    token2 = response2.json()["token"]

    values = {
        "token1": token1,
        "token2": token2,
    }
    return values

def test_permission_change_invalid_token(data):
    '''
    token user is not a global owner
    '''
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token2"],
        "u_id":             2,
        "permission_id":    1
    })
    assert response.status_code ==  403

def test_permission_change_invalid_u_id(data):
    '''
    u_id does not refer to a valid user
    '''
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token1"],
        "u_id":             -1,
        "permission_id":    1
    })
    assert response.status_code == 400

def test_permission_change_invalid_p_id(data):
    '''
    permission_id is invalid
    '''
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token1"],
        "u_id":             1,
        "permission_id":    -1234
    })
    assert response.status_code == 400

# token user is not a global owner, invalid permission_id
def test_permission_change_invalid_p_id_invalid_token(data):
    '''
    the authorised user is not a global owner
    '''
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token2"],
        "u_id":             1,
        "permission_id":    2
    })
    assert response.status_code == 403

def test_http_admin_userpermission_change(data):
    '''
    normal case
    '''
    token1 = data["token1"]
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            token1,
        "u_id":             2,
        "permission_id":    1
    })
    assert response.status_code == 200

def test_already_have_permission(data):
    '''
    when the selected user already has the permissions
    '''
    token1 = data["token1"]
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            token1,
        "u_id":             2,
        "permission_id":    2
    })
    assert response.status_code == 400

def test_only_user():
    '''
    the only global user is being downgraded to normal member
    '''
    requests.delete(url + 'clear/v1')

    response1 = requests.post(url + "auth/register/v2", json={
        'email' : 'czt@gmail.com','password' : 'czt0128',
        'name_first' : 'zhitao','name_last' : 'chen'
    })
    token1 = response1.json()["token"]

    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            token1,
        "u_id":             response1.json()["auth_user_id"],
        "permission_id":    2
    })
    assert response.status_code == 400