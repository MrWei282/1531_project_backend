"""
This script contains a function that returns detail about the user with the given u_id
"""

from src.data_store import data_store
from src.validity_check import token_validity
from src.persistence import save_data
from datetime import timezone
import datetime

def collect_user_info(auth_user_id):
    """
    Given an auth_user_id, returns relevant detail about the user.

    Arguments:
        auth_user_id (int) - u_id of the user

    Exception:
        None

    Returns Value:
        returns a dictionary containing auth_user_id, email, name_first, name_last, and handle_str
    """

    store = data_store.get()
    users = store["users"]

    user_info = {}
    for user in users:
        if auth_user_id == user["u_id"]:
            user_info = {
                "u_id": auth_user_id,
                "email": user["email"],
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle_str"],
            }

    return user_info

def update_user_joined(token, auth_user_id, channel_id, dm_id):
    store = data_store.get()
    users = store["users"]
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_stamp = utc_time.timestamp()
    channel_change = False
    for user in users:
        if auth_user_id == user["u_id"]:
            if int(dm_id) == -1:
                user["joined_channels"].append(channel_id)
                num_channels_joined = len(user["joined_channels"])
                channel_change = True
            elif int(dm_id) == -2:
                user["joined_channels"].remove(channel_id)
                num_channels_joined = len(user["joined_channels"])
                channel_change = True
            elif int(channel_id) == -1:
                user["joined_dms"].append(dm_id)
                num_dms_joined = len(user["joined_dms"])
            elif int(channel_id) == -2:
                user["joined_dms"].remove(dm_id)
                num_dms_joined = len(user["joined_dms"])
            break
    if channel_change:
        channels_joined = {
            "num_channels_joined": num_channels_joined,
            "time_stamp": time_stamp
        }
        user["user_stats"]["channels_joined"].append(channels_joined)
        involvement_rate = user_stats_v1(token)["involvement_rate"]
        user["user_stats"]["involvement_rate"] = involvement_rate
    else:
        dms_joined = {
            "num_dms_joined": num_dms_joined,
            "time_stamp": time_stamp
        }
        user["user_stats"]["dms_joined"].append(dms_joined)
        involvement_rate = user_stats_v1(token)["involvement_rate"]
        user["user_stats"]["involvement_rate"] = involvement_rate

    # store data
    data_store.set(store)
    save_data()

    return

def user_stats_v1(token):
    """_summary_

    Args:
        token (str): code ID
        
        return:
        channels_joined: [{num_channels_joined, time_stamp}],
        dms_joined: [{num_dms_joined, time_stamp}], 
        messages_sent: [{num_messages_sent, time_stamp}], 
        involvement_rate 
    """
    #check the parameters and obtain u_id
    auth_user_id = token_validity(token)
    store = data_store.get()
    users = store["users"]
    msg_list = store["messages"]
    dm_list = store["dms"]
    channel_list = store["channels"]
    num_messages_sent = 0
    num_total_msg = 0

    for user in users:
        if auth_user_id == user["u_id"]:
            num_channels = len(channel_list)
            num_dms = len(dm_list)

            for msg_info in msg_list:
                for each_msg in msg_info["all_msg"]:
                    num_total_msg += 1
                    if each_msg["u_id"] == auth_user_id:
                        num_messages_sent += 1

            num_channels_joined = len(user["joined_channels"])
            num_dms_joined = len(user["joined_dms"])
            
            if num_channels + num_dms + num_total_msg == 0:
                involvement_rate = 0
            elif num_channels_joined + num_dms_joined + num_messages_sent > num_channels + num_dms + num_total_msg:
                involvement_rate = 1
            elif num_channels_joined + num_dms_joined + num_messages_sent <= num_channels + num_dms + num_total_msg:
                involvement_rate = (num_channels_joined + num_dms_joined + num_messages_sent)/(num_channels + num_dms + num_total_msg)
            user["user_stats"]["involvement_rate"] = involvement_rate
            user_stats = user["user_stats"]
            break

    return user_stats

def message_send_counter(token, auth_user_id):
    """_summary_

    Args:
        auth_user_id (_type_): user id

    Returns:
        no return but add total number of messages have been sent
    """
    store = data_store.get()
    users = store["users"]
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_stamp = utc_time.timestamp()
    for user in users:
        if user["u_id"] == auth_user_id:
            break
    
    message_send_curr = len(user["user_stats"]["messages_sent"]) + 1
    messages_sent = {
        "num_messages_sent": message_send_curr,
        "time_stamp": time_stamp
    }
    user["user_stats"]["messages_sent"].append(messages_sent)
    
    involvement_rate = user_stats_v1(token)["involvement_rate"]
    user["user_stats"]["involvement_rate"] = involvement_rate
    
    # store data
    data_store.set(store)
    save_data()
    
    return

def users_stats_v1(token):
    #check the parameters and obtain u_id
    token_validity(token)
    store = data_store.get()
    workspace_stats = store["workspace_stats"]
    workspace_stats["utilization_rate"] = get_utilization_rate()
    
    return workspace_stats

def update_ch_dm_workspace(is_channel):
    store = data_store.get()
    workspace_stats = store["workspace_stats"]
    channels= store["channels"]
    dms = store["dms"]
    
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_stamp = utc_time.timestamp()

    if is_channel:
        num_channels_exist = len(channels)
        workspace_stats["channels_exist"].append({
            "num_channels_exist": num_channels_exist,
            "time_stamp": time_stamp
            })
    elif not is_channel:
        num_channels_exist = len(dms)
        workspace_stats["dms_exist"].append({
            "num_dms_exist": num_channels_exist,
            "time_stamp": time_stamp
            })
    # store data
    data_store.set(store)
    save_data()
    
    return

def update_msg_sent_workspace(is_add):
    store = data_store.get()
    workspace_stats = store["workspace_stats"]
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_stamp = utc_time.timestamp()
    if is_add:
        workspace_stats["messages_exist"].append({
            "num_messages_exist": 1,
            "time_stamp": time_stamp,
        })
    else:
        workspace_stats["messages_exist"].append({
                "num_messages_exist": workspace_stats["messages_exist"][-1]["num_messages_exist"] - 1, 
                "time_stamp": time_stamp,
            })
    # store data
    data_store.set(store)
    save_data()
    
    return

def get_utilization_rate():
    '''
    The workspace's utilization, which is a ratio of the number of users who have joined
    at least one channel/DM to the current total number of users, 
    as defined by this pseudocode: num_users_who_have_joined_at_least_one_channel_or_dm / num_users
    '''
    store = data_store.get()
    users = store['users']

    num_users_who_have_joined_at_least_one_channel_or_dm = 0
    num_user = len(users)
    for user in users:
        if user["user_stats"]["involvement_rate"] > 0:
            num_users_who_have_joined_at_least_one_channel_or_dm += 1

    utilization_rate = float(
        num_users_who_have_joined_at_least_one_channel_or_dm / num_user)

    return utilization_rate
