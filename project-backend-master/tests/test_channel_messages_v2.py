"""
Descripte test the functionailty of channel messages.
"""
import pytest
import requests

from src.config import url
@pytest.fixture
def initialise():
    requests.delete(f"{url}/clear/v1")

    response_user_1 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z5343970@gmail.com", 
             "password": "czt20020128", 
             "name_first": "Zhitao",
             "name_last": "Chen"
        })

    response_user_2 = requests.post(
        f"{url}/auth/register/v2", json = {
             "email": "z536@unsw.edu.au", 
             "password": "Aa!F@32(Bc", 
             "name_first": "Tianyu",
             "name_last": "Wei"
        })

    resp_channel_1 = requests.post(
        f"{url}/channels/create/v2", json = {
            "token": response_user_1.json()['token'],
            "name": "unsw discord server",
            "is_public": True
        })

    return {
        "u_1_token": response_user_1.json()['token'],
        "u_2_token": response_user_2.json()['token'],
        "c_pub_1_id": resp_channel_1.json()['channel_id'],
    }

# testing channal mesages empty
def test_channel_message_empty(initialise):

    resp_message_emp = requests.get(
        f"{url}/channel/messages/v2",params ={
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "start" : 0
        })

    assert resp_message_emp.json()["messages"] == []
    assert resp_message_emp.status_code == 200

# channel_id does not refer to a valid channel
def test_channel_messages_invalid_id(initialise):
    """
    Test the functionailty of return value of channel messages,
    with invalid id as input.
    """

    resp_msg_invalid_cha = requests.get(
        f"{url}/channel/messages/v2", params = {
            "token": initialise["u_1_token"],
            "channel_id": 999,
            "start": 0
        })
    assert resp_msg_invalid_cha.status_code == 400

# start is greater than the total number of messages in the channel
def test_channel_messages_invalid_start_larger(initialise):
    """
    Test the functionailty of return value of channel messages,
    with invalid start as input.
    """

    resp_msg_start_larger = requests.get(
        f"{url}/channel/messages/v2", params = {
            "token": initialise["u_1_token"],
            "channel_id": initialise["c_pub_1_id"],
            "start": 70
        })
    assert resp_msg_start_larger.status_code == 400

# channel_id is valid and the authorised user is not a member of the channel
def test_channel_messages_not_member(initialise):
    """
    Test the functionailty of return value of channel messages,
    with unauthorised user as input.
    """

    resp_msg_not_member = requests.get(
        f"{url}/channel/messages/v2", params = {
            "token": initialise["u_2_token"],
            "channel_id": initialise["c_pub_1_id"],
            "start": 0
        })
    assert resp_msg_not_member.status_code == 403

def test_invalid_token(initialise):
    '''To check the raise error functionailty for invalid token.'''

    resp_1 = requests.get(
        f"{url}/channel/messages/v2", params = {
            "token": "invalid_token",
            "channel_id": initialise["c_pub_1_id"],
            "start": 0
        })
    assert resp_1.status_code == 403

    resp_2 = requests.get(
        f"{url}/channel/messages/v2", params = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjF9.GUPqQ_DOSzE4aXkV7C8gnNCmf-V1ti5agmqq0moBtdw",
            "channel_id": initialise["c_pub_1_id"],
            "start": 0
        })
    assert resp_2.status_code == 403
