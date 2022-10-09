"""
message_send_v1
Send a message from the authorised user to the channel specified by channel_id.
message_edit_v1
Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
message_remove_v1
Given a message_id for a message, this message is removed from the channel/DM
"""

from src.data_store import data_store
from src.error import InputError, AccessError
from src.validity_check import token_validity, check_auth_user_channel, check_auth_permission, check_auth_user_dm
from src.persistence import save_data
from src.other import is_dm_valid, tagging
from src.user_info import update_msg_sent_workspace, message_send_counter

from datetime import timezone
# import datetime
import threading as th
import re
import datetime


def message_send_v1(token, channel_id, message):
    """
    Send a message from the authorised user to the channel specified by channel_id.
    Note: Each message should have its own unique ID,
    i.e. no messages should share an ID with another message,
    even if that other message is in a different channel.

    Arguments:
        token (_type_): encode user_id
        channel_id (_type_): channel_id which message should go
        message (_type_): str type should add to channel

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
                    - length of message is less than 1 or over 1000 characters
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns message_id
    """
    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # get all info stored in data_store
    store = data_store.get()
    messages = store["messages"]

    for msg in messages:
        # found the matching channel
        if msg["is_channel"]:
            if channel_id == msg["channel_id"]:
                if len(message) >= 1 and len(message) <= 1000:
                    dt = datetime.datetime.now(timezone.utc)
                    utc_time = dt.replace(tzinfo=timezone.utc)
                    time_sent = utc_time.timestamp()
                    message_id = int(time_sent * 1000000)

                    message_info = {
                        "message_id": message_id,
                        "u_id": auth_user_id,
                        "message": message,
                        "time_sent": time_sent,
                        "reacts": [],
                        "is_pined": False,
                    }
                    reacts = {
                        "react_id": 1,
                        "u_ids": [],
                        "is_this_user_reacted": False
                    }
                    message_info["reacts"].append(reacts)

                    msg["all_msg"].append(message_info)
                    for channel in store["channels"]:
                        if channel_id == channel["channel_id"]:
                            channel["message_id_list"].append(message_id)
                    
                    tagging(auth_user_id, channel_id, -1, message)
                    message_send_counter(token, auth_user_id)
                    update_msg_sent_workspace(True)

                else:
                    raise InputError(
                        "length of message should not less than 1 or over 1000 characters")

    data_store.set(store)
    save_data()
    return {
        "message_id": message_id,
    }


def message_edit_v1(token, message_id, message):
    """
    Given a message, update its text with new text.
    If the new message is an empty string, the message is deleted.

    Arguments:
        token (_type_): encode user_id
        message_id (_type_): message_id which message should go
        message (_type_): str type should add to channel

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
                    - length of message is less than 1 or over 1000 characters
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns Nothing
    """

    auth_user_id = token_validity(token)
    auth_user_permission = check_auth_permission(auth_user_id)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]
    msg_list = store["messages"]

    check_owner = False
    valid_msg_id = False
    channel_id = -1
    # retrieve the channel_id of relevant messaage_id
    for msg in msg_list:
        for msg_info in msg["all_msg"]:
            if message_id == msg_info["message_id"]:
                valid_msg_id = True
                break

    if not valid_msg_id:
        raise InputError("message_id does not refer to a valid message " +
                         "within a channel/DM that the authorised user has joined")

    # check for owner permission
    if msg["is_channel"]:
        channel_id = msg["channel_id"]
        dm_id = -1
        for channel in channels:
            if channel_id == channel["channel_id"]:
                for owner_member in channel["owner_members"]:
                    if auth_user_id == owner_member:
                        check_owner = True
                        break
                break
    elif msg["is_dm"]:
        dm_id = msg["dm_id"]
        channel_id = -1
        for dm in dms:
            if dm_id == dm["dm_id"]:
                if dm["owner"] == auth_user_id:
                    check_owner = True
                break

    # check if user have the right to edit message and do so if he does
    if msg_info["u_id"] == auth_user_id or check_owner or auth_user_permission == 1:
        if message != "" and len(message) <= 1000:
            msg_info["message"] = message
            tagging(auth_user_id, channel_id, dm_id, message)
        elif message == "":
            message_remove_v1(token, message_id)
        else:
            raise InputError(
                "length of message should be over 1000 characters")
    else:
        raise AccessError("You have no right to edit the message")

    data_store.set(store)
    save_data()
    return {
    }


def message_remove_v1(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token (_type_): encode user_id
        message_id (_type_): message_id which message should go

    Exceptions:
        InputError  - message_id does not refer to a valid message within a channel/DM
                      that the authorised user has joined
        AccessError - the message was sent by the authorised user making this request
                    - the authorised user has owner permissions in the channel/DM

    Return Value:
        Returns Nothing
    """

    auth_user_id = token_validity(token)
    auth_user_permission = check_auth_permission(auth_user_id)

    valid_msg_id = False
    same_user = False
    ownerPermission = False

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]
    msg_list = store["messages"]
    dms = store["dms"]

    # retrieve the channel_id of relevant messaage_id
    for msg in msg_list:
        for msg_info in msg["all_msg"]:
            if message_id == msg_info["message_id"]:
                valid_msg_id = True
                break

    if not valid_msg_id:
        raise InputError("message_id does not refer to a valid message " +
                         "within a channel/DM that the authorised user has joined")

    # check for owner permission
    if msg["is_channel"]:
        channel_id = msg["channel_id"]
        for channel in channels:
            if channel_id == channel["channel_id"]:
                for owner_member in channel["owner_members"]:
                    if auth_user_id == owner_member:
                        ownerPermission = True

    elif msg["is_dm"]:
        dm_id = msg["dm_id"]
        for dm in dms:
            if dm_id == dm["dm_id"]:
                if dm["owner"] == auth_user_id:
                    ownerPermission = True

    if msg_info["u_id"] == auth_user_id:
        same_user = True

    if same_user == True or ownerPermission == True or auth_user_permission == 1:
        for channel in channels:
            if message_id in channel["message_id_list"]:
                channel["message_id_list"].remove(message_id)
                msg["all_msg"].remove(msg_info)
                update_msg_sent_workspace(False)
    else:
        raise AccessError("You have no right to remove the message")

    data_store.set(store)
    save_data()
    return {
    }


def message_senddm_v1(token, dm_id, message):
    """
    Send a message from the authorised user to the dm specified by dm_id.
    Note: Each message should have its own unique ID,
    i.e. no messages should share an ID with another message,
    even if that other message is in a different dm.

    Arguments:
        token (_type_): encode user_id
        dm_id (_type_): dm_id which message should go
        message (_type_): str type should add to dm

    Exceptions:
        InputError  - dm_id does not refer to a valid dm
                    - length of message is less than 1 or over 1000 characters
        AccessError - dm_id is valid and the authorised user is not a member of the dm

    Return Value:
        Returns message_id
    """
    # check the validity of token
    auth_user_id = token_validity(token)

    # get all info stored in data_store
    store = data_store.get()
    messages = store["messages"]
    dm_store = store['dms']

    # dm_id does not refer to a valid dm
    if not is_dm_valid(dm_id):
        raise InputError(description="Dm_id does bot refer to a valid dm.")

    # auth_user is not in the dm
    is_dm_member = False
    for dm in dm_store:
        if dm["dm_id"] == dm_id:
            for user_id in dm["all_members"]:
                if user_id == auth_user_id:
                    is_dm_member = True
            break

    if not is_dm_member:
        raise AccessError(
            description="dm_id is valid and the authorised user is not a member of the DM")

    for msg in messages:
        if msg["is_dm"]:
            # found the matching dm
            if dm_id == msg["dm_id"]:
                if len(message) >= 1 and len(message) <= 1000:
                    dt = datetime.datetime.now(timezone.utc)
                    utc_time = dt.replace(tzinfo=timezone.utc)
                    time_sent = utc_time.timestamp()
                    message_id = int(time_sent * 1000000)

                    message_info = {
                        "message_id": message_id,
                        "u_id": auth_user_id,
                        "message": message,
                        "time_sent": time_sent,
                        "reacts": [],
                        "is_pined": False,
                    }
                    reacts = {
                        "react_id": 1,
                        "u_ids": [],
                        "is_this_user_reacted": False
                    }
                    message_info["reacts"].append(reacts)

                    msg["all_msg"].append(message_info)

                    for dm in dm_store:
                        if dm_id == dm["dm_id"]:
                            dm["message_id_list"].append(message_id)
                    
                    tagging(auth_user_id, -1, dm_id, message)
                    message_send_counter(token, auth_user_id)
                    update_msg_sent_workspace(True)

                else:
                    raise InputError(
                        "length of message should not less than 1 or over 1000 characters")

    data_store.set(store)
    save_data()
    return {
        "message_id": message_id,
    }

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future.
    Argument:
        token (string)      -token of user sending the message
        channel_id (int)    -id of channel
        message (string)    -message send by user
        time_sent (int)     -excuted time of message by the user

    return valur:
        { message_id }
    '''
    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    if (len(message) < 1 or len(message) > 1000):
        raise InputError(
            "length of message is less than 1 or over 1000 characters")

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_current = utc_time.timestamp()
    message_id = int(time_current * 1000000)

    # time_current = int(datetime.datetime.utcnow()
    #                    .replace(tzinfo=datetime.timezone.utc).timestamp())
    if time_sent < time_current:
        raise InputError("time_sent is in the past")

    time_interval = int(time_sent - time_current)

    time_later = th.Timer(time_interval, msg_later, [
        token, channel_id, message, message_id, time_sent])

    time_later.start()

    return {
        'message_id': message_id
    }

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future.
    Argument:
        token (string)      -token of user sending the message
        channel_id (int)    -id of channel
        message (string)    -message send by user
        time_sent (int)     -excuted time of message by the user

    return valur:
        { message_id }
    '''
    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of dm and if auth user is in the channel
    check_auth_user_dm(auth_user_id, dm_id)

    if (len(message) < 1 or len(message) > 1000):
        raise InputError(
            "length of message is less than 1 or over 1000 characters")

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_current = utc_time.timestamp()
    message_id = int(time_current * 1000000)

    # time_current = int(datetime.datetime.utcnow()
    #                    .replace(tzinfo=datetime.timezone.utc).timestamp())
    if time_sent < time_current:
        raise InputError("time_sent is in the past")

    time_interval = int(time_sent - time_current)

    time_later = th.Timer(time_interval, msg_later_dm, [
        token, dm_id, message, message_id, time_sent])

    time_later.start()

    return {
        'message_id': message_id
    }

def msg_later(token, channel_id, message, message_id, time_sent):
    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # get all info stored in data_store
    store = data_store.get()
    messages = store["messages"]

    for msg in messages:
        # found the matching channel
        if msg["is_channel"]:
            if channel_id == msg["channel_id"]:
                message_info = {
                    "message_id": message_id,
                    "u_id": auth_user_id,
                    "message": message,
                    "time_sent": time_sent,
                    "is_pined": False,
                    "reacts": [],
                }

                reacts = {
                    "react_id": 1,
                    "u_ids": [],
                    "is_this_user_reacted": False
                }
                message_info["reacts"].append(reacts)

                msg["all_msg"].append(message_info)
                message_send_counter(token, auth_user_id)
                update_msg_sent_workspace(True)

                for channel in store["channels"]:
                    if channel_id == channel["channel_id"]:
                        channel["message_id_list"].append(message_id)

    data_store.set(store)
    save_data()
    return


def msg_later_dm(token, dm_id, message, message_id, time_sent):
    # check the validity of token
    auth_user_id = token_validity(token)

    # # check for validity of channel id and if auth user is in the channel
    # check_auth_user_dm(auth_user_id, dm_id)

    # get all info stored in data_store
    store = data_store.get()
    messages = store["messages"]

    for msg in messages:
        # found the matching channel
        if msg["is_dm"]:
            if dm_id == msg["dm_id"]:
                message_info = {
                    "message_id": message_id,
                    "u_id": auth_user_id,
                    "message": message,
                    "time_sent": time_sent,
                    "is_pined": False,
                    "reacts": [],
                }

                reacts = {
                    "react_id": 1,
                    "u_ids": [],
                    "is_this_user_reacted": False
                }
                message_info["reacts"].append(reacts)

                msg["all_msg"].append(message_info)
                message_send_counter(token, auth_user_id)
                update_msg_sent_workspace(True)

                for dm in store["dms"]:
                    if dm_id == dm["dm_id"]:
                        dm["message_id_list"].append(message_id)

    data_store.set(store)
    save_data()
    return

def message_react_v1(token, message_id, react_id):
    """_summary_

    Args:
        token (_type_): _description_
        message_id (_type_): _description_
        react_id (_type_): _description_
    """
    auth_user_id = token_validity(token)
    store = data_store.get()
    msg_list = store["messages"]
    users = store["users"]

    user_valid = False
    message_vaild = False

    if react_id != 1:
        raise InputError(description = "react_id must be 1")
    else:
        for msg in msg_list:
            for msg_info in msg["all_msg"]:
                if message_id == msg_info["message_id"]:
                    message_vaild = True
                    break

    if not message_vaild:
        raise InputError(description = "message_id is not a vaild id")

    for user in users:
        if auth_user_id == user["u_id"]:
            break

    if msg["is_channel"]:
        for channel_id in user["joined_channels"]:
            if channel_id == msg["channel_id"]:
                user_valid = True
    else:
        for dm_id in user["joined_dms"]:
            if dm_id == msg["dm_id"]:
                user_valid = True

    if not user_valid:
        raise InputError(description = "message_id is not a valid message within a channel or DM that the authorised user has joined")

    for reacts in msg_info["reacts"]:
        if react_id == reacts["react_id"]:
            for reacted_user_id in reacts["u_ids"]:
                if auth_user_id == reacted_user_id:
                    raise InputError(description = "the message already contains a react with ID react_id from the authorised user")
            break

    reacts["u_ids"].append(auth_user_id)
        
    data_store.set(store)
    save_data()

def message_unreact_v1(token, message_id, react_id):
    """_summary_

    Args:
        token (_type_): _description_
        message_id (_type_): _description_
        react_id (_type_): _description_
    """    
    auth_user_id = token_validity(token)
    store = data_store.get()
    msg_list = store["messages"]
    users = store["users"]

    user_valid = False
    message_vaild = False

    if react_id != 1:
        raise InputError(description = "react_id must be 1")
    else:
        for msg in msg_list:
            for msg_info in msg["all_msg"]:
                if message_id == msg_info["message_id"]:
                    message_vaild = True
                    break

    if not message_vaild:
        raise InputError(description = "message_id is not a vaild id")

    for user in users:
        if auth_user_id == user["u_id"]:
            break

    if msg["is_channel"]:
        for channel_id in user["joined_channels"]:
            if channel_id == msg["channel_id"]:
                user_valid = True
    else:
        for dm_id in user["joined_dms"]:
            if dm_id == msg["dm_id"]:
                user_valid = True

    if not user_valid:
        raise InputError(description = "message_id is not a valid message within a channel or DM that the authorised user has joined")

    already_reacted = False
    for reacts in msg_info["reacts"]:
        if react_id == reacts["react_id"]:
            for reacted_user_id in reacts["u_ids"]:
                if auth_user_id == reacted_user_id:
                    already_reacted = True
                    break
            break

    if not already_reacted:
        raise InputError(description = "the message does not contain a react with ID react_id from the authorised user")

    reacts["u_ids"].remove(auth_user_id)
        
    data_store.set(store)
    save_data()

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """_summary_

    Args:
        token (_type_): _description_
        og_message_id (_type_): _description_
        message (_type_): _description_
        channel_id (_type_): _description_
        dm_id (_type_): _description_
    """
    auth_user_id = token_validity(token)
    store = data_store.get()
    msg_list = store["messages"]
    dm_list = store["dms"]
    channel_list = store["channels"]
    channel_id_valid = False
    is_in_channel = False
    is_in_dm = False
    og_message_in_channel = False
    og_message_in_dm = False
    dm_id_valid = is_dm_valid(dm_id)
    if channel_id == -1:
        if dm_id_valid == False:
            raise InputError(description="Dm_id does bot refer to a valid dm.")

    if dm_id == -1:
        for msg in msg_list:
            for msg_info in msg["all_msg"]:
                if og_message_id == msg_info["message_id"]:
                    channel_id_valid = True
                    break
                
    if channel_id_valid == False and dm_id_valid == False:
        raise InputError(description="channel_id and dm_id are invalid.")

    if dm_id != -1 and channel_id != -1:
        raise InputError(description="neither channel_id nor dm_id are -1")

    if dm_id == -1:
        for channel in channel_list:
            for each_message_id_in_channel in channel["message_id_list"]:
                if og_message_id == each_message_id_in_channel:
                    og_message_in_channel = True
    if channel_id == -1:
        for dm in dm_list:
            for each_message_id_in_dm in dm["message_id_list"]:
                if og_message_id == each_message_id_in_dm:
                    og_message_in_dm = True
    if og_message_in_channel == False and og_message_in_dm == False:
        raise InputError(description="og_message_id does not refer to a valid" +
                                 " message within a channel/DM that the authorised user has joined")

    if len(message) > 1000:
        raise InputError(description="length of message is more than 1000 characters")

    og_message = ""

    if channel_id == -1 and dm_id != -1:
        if dm_id_valid == True:
            for each_dm in dm_list:
                if dm_id == each_dm["dm_id"]:
                    for dm_member in each_dm["all_members"]:
                        if auth_user_id == dm_member:
                            is_in_dm = True
                        if is_in_dm == False:
                            raise AccessError(description="user not in that dm")
    if channel_id != -1 and dm_id == -1:
        if channel_id_valid == True:
            for channel in channel_list:
                if channel_id == channel["channel_id"]:
                    for channel_member in channel["all_members"]:
                        if auth_user_id == channel_member:
                            is_in_channel = True
                        if is_in_channel == False:
                            raise AccessError(description="user not in that channel")

    if is_in_channel == True:
        for msg in msg_list:
            for each_og_message in msg["all_msg"]:
                if og_message_id == each_og_message["message_id"]:
                    og_message = each_og_message["message"]
        message = og_message + " " + message
        message_id = message_send_v1(token, channel_id, message)
        
    if is_in_dm == True:
        for msg in msg_list:
            for each_og_message in msg["all_msg"]:
                if og_message_id == each_og_message["message_id"]:
                    og_message = each_og_message["message"]
        message = og_message + " " + message
        message_id = message_senddm_v1(token, dm_id, message)
    return message_id

def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned".
    Arguments:
        token       (str): the given token
        message_id  (int): the given message_id
    Exceptions:
        InputError:
            - message_id is not a valid message within a channel or DM
                that the authorised user has joined
            - the message is already pinned
        AccessError:
            - message_id refers to a valid message in a joined channel/DM and
                the authorised user does not have owner permissions in the channel/DM
    Return Value:
        empty dictionary.
    '''
    auth_user_id = token_validity(token)
    auth_global = check_auth_permission(auth_user_id)

    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]
    messages = store["messages"]
    

    valid_joined = False    
    is_channel = False
    is_dm = False 
    
    for user in users:
        if auth_user_id == user["u_id"]:
            break
    
    # check message_id is within a channel/dm that the user has joined
    # find location of message_id
    for message in messages:
        for msg_info in message["all_msg"]:
            if message_id == msg_info["message_id"]:
                if message["is_channel"] == True:
                    is_channel = True
                    channel_id = message["channel_id"]
                    for joined_channel in user["joined_channels"]:
                        if joined_channel == channel_id:
                            valid_joined = True
                            break
                    
                if message["is_dm"] == True:
                    is_dm = True
                    dm_id = message["dm_id"]
                    for joined_dm in user["joined_dms"]:
                        if joined_dm == dm_id:
                            valid_joined = True
                            break
                
    
    if valid_joined == False:
        raise InputError(description="message_id not within a channel/dm that the user has joined")
    
    is_owner = False
    if is_channel:
        for channel in channels:
            if channel_id == channel["channel_id"]:
                for owner in channel["owner_members"]:
                    if owner == auth_user_id:
                        is_owner = True
                        break
    elif is_dm:
        for dm in dms:
            if dm_id == dm["dm_id"]:
                if auth_user_id == dm["owner"]:
                    is_owner = True
                    break
    
    if not is_owner or auth_global != 1:
        raise AccessError(description="is not owner_members")
    
    if msg_info["is_pined"]:
        raise InputError(description="The message is already pinned")
    else:
        msg_info["is_pined"] = True

    data_store.set(store)
    save_data()
    return 
def message_unpin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "unpinned".
    Arguments:
        token       (str): the given token
        message_id  (int): the given message_id
    Exceptions:
        InputError:
            - message_id is not a valid message within a channel or DM
                that the authorised user has joined
            - the message is already not pinned
        AccessError:
            - message_id refers to a valid message in a joined channel/DM and
                the authorised user does not have owner permissions in the channel/DM
    Return Value:
        empty dictionary.
    '''
    auth_user_id = token_validity(token)
    auth_global = check_auth_permission(auth_user_id)

    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]
    messages = store["messages"]
    

    valid_joined = False    
    is_channel = False
    is_dm = False 
    
    for user in users:
        if auth_user_id == user["u_id"]:
            break
    
    # check message_id is within a channel/dm that the user has joined
    # find location of message_id
    for message in messages:
        for msg_info in message["all_msg"]:
            if message_id == msg_info["message_id"]:
                if message["is_channel"] == True:
                    is_channel = True
                    channel_id = message["channel_id"]
                    for joined_channel in user["joined_channels"]:
                        if joined_channel == channel_id:
                            valid_joined = True
                            break
                    
                if message["is_dm"] == True:
                    is_dm = True
                    dm_id = message["dm_id"]
                    for joined_dm in user["joined_dms"]:
                        if joined_dm == dm_id:
                            valid_joined = True
                            break
                
    
    if valid_joined == False:
        raise InputError(description="message_id not within a channel/dm that the user has joined")
    
    is_owner = False
    if is_channel:
        for channel in channels:
            if channel_id == channel["channel_id"]:
                for owner in channel["owner_members"]:
                    if owner == auth_user_id:
                        is_owner = True
                        break
    elif is_dm:
        for dm in dms:
            if dm_id == dm["dm_id"]:
                if auth_user_id == dm["owner"]:
                    is_owner = True
                    break
    
    if not is_owner or auth_global != 1:
        raise AccessError(description="is not owner_members")
    
    if msg_info["is_pined"] == False:
        raise InputError(description="The message is not already pinned")
    else:
        msg_info["is_pined"] = False

    data_store.set(store)
    save_data()
    return 
