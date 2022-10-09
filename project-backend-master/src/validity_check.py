"""
This script contains a function that check if the auth_user is valid
"""

from src.data_store import data_store
from src.generate_token import decode_jwt

from src.error import InputError, AccessError


def token_validity(token):
    """
    Given an token, check if the token matches the info stored in data base

    Arguments:
        token (str) - token of the user

    Exception:
        AccessError - Occurs when auth_user is not registered
                    - Occurs when session_id_list is empty

    Returns Value:
        returns auth_user_id(int)
    """

    store = data_store.get()
    users = store["users"]

    valid_token = False
    token_info = decode_jwt(token)

    for user in users:
        if token_info["auth_user_id"] == user["u_id"]:
            # user has an empty session_id_list
            if not user["session_id_list"]:
                raise AccessError(description="user has not login")

            if token_info["session_id"] == user["session_id_list"][-1]:
                valid_token = True
                return int(token_info["auth_user_id"])

    if not valid_token:
        raise AccessError(description="token is not valid")


def check_auth_user_channel(auth_user_id, channel_id):
    store = data_store.get()
    channels = store["channels"]

    # search for a matching channel_id in the list of channels
    valid_channel_id = False
    auth_user_joined = False

    for channel in channels:
        if channel_id == channel["channel_id"]:
            valid_channel_id = True
            # found the matching channel
            for member in channel["all_members"]:
                # check for if auth_user is already a member of the channel
                if auth_user_id == member:
                    auth_user_joined = True
                    break
            break

    # no matching channel_id found
    if not valid_channel_id:
        raise InputError(
            description="Channel_id does not refer to a valid channel")

    if not auth_user_joined:
        raise AccessError(
            description="Authorised user is not a member of the channel")

    return


def check_u_id_channel(u_id, channel_id):
    # get all info stored in data_store
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # check if u_id is valid
    valid_user = False
    for user in users:
        if u_id == user["u_id"]:
            valid_user = True
            break
    if not valid_user:
        raise InputError(description="u_id does not refer to a valid user")

    is_member = False
    # check if u_id refer to a member in the channel
    for channel in channels:
        if channel_id == channel["channel_id"]:
            for member in channel["all_members"]:
                if u_id == member:
                    is_member = True
                    return is_member

    return is_member


def check_auth_permission(auth_user_id):
    # get all info stored in data_store
    store = data_store.get()
    users = store["users"]

    # check the global permission of auth user
    auth_user_permission = 2
    for user in users:
        if auth_user_id == user["u_id"]:
            auth_user_permission = user["permission_id"]
            return int(auth_user_permission)

def check_auth_user_dm(auth_user_id, dm_id):
    store = data_store.get()
    dms = store["dms"]

    # search for a matching channel_id in the list of channels
    valid_dm_id = False
    auth_user_joined = False

    for dm in dms:
        if dm_id == dm["dm_id"]:
            valid_dm_id = True
            # found the matching channel
            for member in dm["all_members"]:
                # check for if auth_user is already a member of the channel
                if auth_user_id == member:
                    auth_user_joined = True
                    break
            break
    # no matching channel_id found
    if not valid_dm_id:
        raise InputError(
            description="dm_id does not refer to a valid dm")

    if not auth_user_joined:
        raise AccessError(
            description="Authorised user is not a member of the dm")

    return
