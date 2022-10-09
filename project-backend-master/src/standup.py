from src.data_store import data_store
from src.error import InputError
from src.validity_check import token_validity, check_auth_user_channel
from src.persistence import save_data
from threading import Timer
from datetime import timezone
import datetime

def terminate_standup(auth_user_id, channel_id, message_id, time_finish):
    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]
    messages = store["messages"]

    # terminate the standup
    for channel in channels:
        if channel_id == channel["channel_id"]:
            standup_msg = channel["standup_msg"]
            channel["standup_msg"] = []
            channel["message_id_list"].append(message_id)
            channel["is_standup_active"] = False
            channel["standup_time_finish"] = -1

    # store the standup messages
    for msg in messages:
        if msg["is_channel"]:
            if channel_id == msg["channel_id"]:
                standup_info = {
                    "message_id": message_id,
                    "u_id": auth_user_id,
                    "message": standup_msg,
                    "time_sent": time_finish,
                    "is_pinned": False,
                    "reacts": [],
                }
                reacts = {
                        "react_id": 1,
                        "u_ids": [],
                        "is_this_user_reacted": False
                    }
                standup_info["reacts"].append(reacts)
                
                msg["all_msg"].append(standup_info)
                break

    # store data
    data_store.set(store)
    save_data()

    return

def standup_start_v1(token, channel_id, length):
    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    if length < 0:
        raise InputError(description = "length is a negative integer")

    if standup_active_v1(token, channel_id)["is_active"]:
        raise InputError(description = "an active standup is currently running in the channel")

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_finish = utc_time.timestamp() + length
    message_id = int(time_finish * 1000000)

    # setup for a standup
    for channel in channels:
        if channel_id == channel["channel_id"]:
            channel["is_standup_active"] = True
            channel["standup_time_finish"] = time_finish

    # started the standup
    Timer(length, terminate_standup, [auth_user_id, channel_id, message_id, time_finish]).start()

    # store data
    data_store.set(store)
    save_data()

    return time_finish
    
def standup_active_v1(token, channel_id):
    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]

    for channel in channels:
        if channel_id == channel["channel_id"]:
            is_active = channel["is_standup_active"]
            if is_active:
                time_finish = channel["standup_time_finish"]
            else:
                time_finish = None

    return {
        "is_active": is_active,
        "time_finish": time_finish,
    }

def standup_send_v1(token, channel_id, message):
    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    if not standup_active_v1(token, channel_id)["is_active"]:
        raise InputError(description = "an active standup is not currently running in the channel")

    if len(message) > 1000:
        raise InputError(description = "length of message is over 1000 characters")

    # get all info stored in data_store
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    for user in users:
        if auth_user_id == user["u_id"]:
            msg_sender_handle = user["handle_str"]

    standup_msg = f"{msg_sender_handle}: {message}\n"
    for channel in channels:
        if channel_id == channel["channel_id"]:
            channel["standup_msg"].append(standup_msg)

    # store data
    data_store.set(store)
    save_data()

    return