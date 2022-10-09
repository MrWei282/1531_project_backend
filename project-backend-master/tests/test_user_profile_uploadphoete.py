import pytest
import requests
from src.config import url

IMG_URL = "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fimg.jj20.com%2Fup%2Fallimg%2F1113%2F052420110515%2F200524110515-2-1200.jpg&amp;refer=http%3A%2F%2Fimg.jj20.com&amp;app=2002&amp;size=f9999,10000&amp;q=a80&amp;n=0&amp;g=0n&amp;fmt=auto?sec=1652863274&amp;t=47159519b672576aff1e3b93614a6a45"
PNG_FILE = "https://uploads.guim.co.uk/2018/01/31/TheGuardian_AMP.png"

@pytest.fixture
def initial_setup():
    requests.delete(url + "clear/v1")

    auth_register_url = url + "auth/register/v2"

    user0_response = requests.post(auth_register_url, json={      
        "email":        "czt@gmail.com", 
        "password":     "abc1234",
        "name_first":   "zhitao", 
        "name_last":    "chen"
    })
    user0 = user0_response.json()
    user0_token = user0["token"]

    user1_response = requests.post(auth_register_url, json={      
        "email":        "czt2@gmail.com", 
        "password":     "abc1234",
        "name_first":   "linbo", 
        "name_last":    "chen"
    })
    user1 = user1_response.json()
    user1_token = user1["token"]
    user1_id = user1["auth_user_id"]

    return {
        "user0_token":  user0_token,
        "user1_token":  user1_token,
        "user1_id":     user1_id
    }

def test_invalid_token(initial_setup):
    response = requests.post(url + "user/profile/uploadphoto/v1", json={
        "token":    "invalid_token",
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    400,
        "y_end":    400
    })
    assert response.status_code == 403


def test_working(initial_setup):
    user0_token = initial_setup["user0_token"]
    user1_token = initial_setup["user1_token"]

    response = requests.post(url + "user/profile/uploadphoto/v1", json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    100,
        "y_end":    100
    })
    assert response.status_code == 200

    response = requests.post(url + "user/profile/uploadphoto/v1", json={
        "token":    user0_token,
        "img_url":  IMG_URL,
        "x_start":  50,
        "y_start":  50,
        "x_end":    100,
        "y_end":    120
    })
    assert response.status_code == 200
