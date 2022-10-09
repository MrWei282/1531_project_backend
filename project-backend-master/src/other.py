"""
This script contains a function resets the data base
"""

from src.data_store import data_store
from src.persistence import save_data
from src.generate_token import reset_session
from src.validity_check import token_validity
import re
from datetime import timezone
import datetime


def clear_v1():
    """
    Resets the data base

    Arguments:
        None

    Exception:
        None

    Returns Value:
        returns none
    """
    reset_session()

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_stamp = utc_time.timestamp()
    
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['messages'] = []
    store['dms'] = []
    store['workspace_stats'] = {'channels_exist': [{
                            "num_channels_exist": 0,
                            "time_stamp": time_stamp
                        }],
                        'dms_exist': [{
                            "num_dms_exist": 0,
                            "time_stamp": time_stamp
                        }],
                        'messages_exist': [{
                            "num_messages_exist": 0,
                            "time_stamp": time_stamp
                        }],
                        'utilization_rate': 0,
                        }
    data_store.set(store)
    save_data()


def generate_dm_name(all_members):
    '''
    Generate an alphabetically-sored, comma-and-space-seperated
    list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.
    Args:
        all_members (list)  - list of added users include creator of the dm
    Returns:
        name (str)  - alphabetically-sored, comma-and-space-seperated
                      list of user handles name string
    '''
    store = data_store.get()
    users = store['users']
    name_list = []

    for member in all_members:
        for user in users:
            if member == user['u_id']:
                name_list.append(user['handle_str'])

    name = ', '.join(sorted(name_list))
    return name


def verify_user_id(auth_user_id):
    """ Helper function that verifies that the user exists in the data store,
        if in data store returns true else false.
        Arguments:
            auth_user_id (int)    - The user id of the user being verified.
        Return Value:
            Returns True on user id being found.
            Returns False on user id not being found.
    """
    is_authorised = False
    store = data_store.get()

    user_store = store['users']
    for user in user_store:
        if user['u_id'] == auth_user_id:
            is_authorised = True
            return is_authorised
    return is_authorised

def is_dm_valid(dm_id):
    '''
    Check whether the given dm is in dms in data store or not
    Args:
        dm_id (int)         -Dm ID of the dm the user is a member of

    Returns:
        is_dm_valid (bool)  -whether the dm in dms in dm store or not (True/False)
    '''
    is_dm_valid = False
    store = data_store.get()
    dm_store = store['dms']

    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            is_dm_valid = True

    return is_dm_valid

def notification_v1(token):
    # check the validity of token
    auth_user_id = token_validity(token)

    # get all info stored in data_store
    store = data_store.get()
    users = store["users"]

    for user in users:
        if auth_user_id == user["u_id"]:
            notifications = user["notifications"]
            break

    return_notifications = notifications[:20]
    return_notifications.reverse()

    return return_notifications

def tagging(auth_user_id, channel_id, dm_id, message):
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]

    # find all handle to tag in a message
    to_tag = re.findall(r'@(.*?)\W+', message)

    last_tag_position = message.rfind('@')
    if last_tag_position != -1:
        last_tag = re.split('\\W+', message[last_tag_position + 1:])[0]

    if last_tag_position != -1 and to_tag == []:
        to_tag.append(last_tag)
    elif last_tag_position != -1 and to_tag != []:
        if to_tag[-1] != last_tag:
            to_tag.append(last_tag)
    else:
        return
    to_tag = list(dict.fromkeys(to_tag))

    # find auth_user's handle for notification display
    for user in users:
        if auth_user_id == user["u_id"]:
            auth_str = user["handle_str"]
            break

    # only shows the first 20 chars for notification message
    message = message[:20]

    if dm_id == -1:
        for channel in channels:
            if channel_id == channel["channel_id"]:
                channel_name = channel["name"]
                break
        for tag_str in to_tag:
            for user in users:
                if tag_str == user["handle_str"]:
                    for joined_channel in user["joined_channels"]:
                        if joined_channel == channel_id:
                            notification_info = {
                                "channel_id": channel_id,
                                "dm_id": -1,
                                "notification_message": f"{auth_str} tagged you in {channel_name}: {message}"
                            }
                            user["notifications"].append(notification_info)
                            break
                    break
    elif channel_id == -1:
        for dm in dms:
            if dm_id == dm["dm_id"]:
                dm_name = dm["name"]
                break
        for tag_str in to_tag:
            for user in users:
                if tag_str == user["handle_str"]:
                    for joined_dm in user["joined_dms"]:
                        if joined_dm == dm_id:
                            notification_info = {
                                "channel_id": -1,
                                "dm_id": dm_id,
                                "notification_message": f"{auth_str} tagged you in {dm_name}: {message}"
                            }
                            user["notifications"].append(notification_info)
                            break
                    break
    data_store.set(store)
    save_data()
    return
