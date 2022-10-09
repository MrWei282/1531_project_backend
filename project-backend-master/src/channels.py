"""
This script contains three functions that allow auth_user to create a channel, 
list a channel that the user is in, and listall all stored channel
"""

from src.data_store import data_store
from src.error import InputError
from src.validity_check import token_validity
from src.persistence import save_data
from src.user_info import update_user_joined, update_ch_dm_workspace

def channels_list_v2(token):
    """
    Provide a list of all channels (and their associated details)
    that the authorised user is part of.

    Arguments:
        token (int) - token of the user

    Exceptions:
        NA

    Return Value:
        Returns a list of dictionaries, where each dictionary contains types { channels}
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # get all info stored in data_store
    data = data_store.get()
    channels = data["channels"]

    # check all channels that has auth_user_id in it
    associated_channels = []
    for channel in channels:
        for member in channel["all_members"]:
            if auth_user_id == member:
                # store detail about associated channel to a list
                channel_detail = {
                    "channel_id": channel["channel_id"],
                    "name": channel["name"]
                }
                associated_channels.append(channel_detail)

    return {
        "channels": associated_channels,
    }


def channels_listall_v2(token):
    '''
    Provide a list of all channels, including private channels, (and their associated details)

    Arguments:
        token (int) - token of the user

    Exceptions:
        NA

    Return:
        Returns a list of dictionaries, where each dictionary contains types { channels}
    '''

    # check the validity of auth_user
    token_validity(token)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]

    # create a list to store the detail of all channels
    channels_listall = []
    for channel in channels:
        channel_detail = {
            "channel_id": channel["channel_id"],
            "name": channel['name']
        }
        channels_listall.append(channel_detail)

    return {
        'channels': channels_listall,
    }

def channels_create_v2(token, name, is_public):
    """
    Creates a new channel with the given name that is either a public or private channel.
    The user who created it automatically joins the channel.

    Arguments:
        token        (string)  - token of the user
        name         (string)  - name of the channel
        is_public    (boolean) - determines the channel is public or private

    Exceptions:
        InputError  - ength of name is less than 1 or more than 20 characters

    Return Value:
        Returns a dictionary containing channel_id
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]

    # check for valid channel name length
    len_channel_name = len(name)
    if (len_channel_name < 1 or len_channel_name > 20):
        raise InputError(description = "length of channel name must be between 1 and 20")

    # generate channel_id
    channel_id = len(channels) + 1

    # store data
    channel_dict = {
        "name": name,
        "is_public": bool(is_public),
        "channel_id": int(channel_id),
        "owner_members": [auth_user_id],
        "all_members": [auth_user_id],
        "message_id_list": [],
        "is_standup_active": False,
        "standup_time_finish": -1,
        "standup_msg": [],
    }
    channels.append(channel_dict)

    init_msg = {
        "channel_id": channel_id,
        "is_channel": True,
        "is_dm": False,
        "all_msg": []
    }
    
    store["messages"].append(init_msg)
    update_user_joined(token, auth_user_id, channel_id, -1)
    update_ch_dm_workspace(True)

    data_store.set(store)
    save_data()

    return {
        "channel_id": int(channel_id),
    }
