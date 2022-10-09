"""
This script contains four functions that allow auth user to
invite other user to a channel, join a channel,
show detail about a channel, display stored messages from a channel,
channel leave function,channel addowner and channel removeowner
"""

from src.data_store import data_store
from src.error import InputError, AccessError
from src.validity_check import token_validity, check_auth_user_channel, check_u_id_channel, check_auth_permission
from src.user_info import collect_user_info, update_user_joined
from src.persistence import save_data


def channel_invite_v2(token, channel_id, u_id):
    """
    Invites a user with ID u_id to join a channel with ID channel_id.
    Once invited, the user is added to the channel immediately.
    In both public and private channels, all members are able to invite users.

    Arguments:
        token        (string) - token of the inviter
        channel_id   (int) - id of the channel to join
        u_id         (int) - u_id of the invitee

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
                    - u_id does not refer to a valid user
                    - u_id refers to a user who is already a member of the channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns nothing
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # check if u_id is valid and if u_id refer to a user already in the channel
    is_member = check_u_id_channel(u_id, channel_id)
    if is_member:
        raise InputError(
            description="The invitee is already a member of the channel")

    # get all info stored in data_store
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # search for a matching channel_id in the list of channels
    for channel in channels:
        if channel_id == channel["channel_id"]:
            # user joins channel
            channel_name = channel["name"]
            channel["all_members"].append(u_id)
            update_user_joined(token, u_id, channel_id, -1)
            break

    for user in users:
        if auth_user_id == user["u_id"]:
            auth_str = user["handle_str"]
            break
    for user in users:
        if u_id == user["u_id"]:
            notification_info = {
                "channel_id": channel_id,
                "dm_id": -1,
                "notification_message": f"{auth_str} added you to {channel_name}"
            }
            user["notifications"].append(notification_info)
            break
    
    # store data
    data_store.set(store)
    save_data()

    return {
    }


def channel_details_v2(token, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a member of,
    provide basic details about the channel.

    Arguments:
        token        (int) - token of the inviter
        channel_id   (int) - id of the channel to join

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns a dictionaries containing channel name, channel type, details about owner_members,
        and details about all_members
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # get data
    data = data_store.get()
    channels = data["channels"]

    # search for a matching channel_id in the list of channels
    channel_details = {}
    for channel in channels:
        # found matching channel
        if channel["channel_id"] == channel_id:
            channel_details["name"] = channel["name"]
            channel_details["is_public"] = channel["is_public"]
            channel_details["owner_members"] = []
            for owner in channel["owner_members"]:
                # collect data about owner
                channel_details["owner_members"].append(
                    collect_user_info(owner))
            channel_details["all_members"] = []
            for member in channel["all_members"]:
                # collect data about owner
                channel_details["all_members"].append(
                    collect_user_info(member))
            break

    return channel_details


def channel_messages_v2(token, channel_id, start):
    """
    Given a channel with ID channel_id that the authorised user is a member of,
    return up to 50 messages between index "start" and "start + 50".
    Message with index 0 is the most recent message in the channel.
    This function returns a new index "end" which is the value of "start + 50", or,
    if this function has returned the least recent messages in the channel,
    returns -1 in "end" to indicate there are no more messages to load after this return.

    Arguments:
        token        (int) - token of the inviter
        channel_id   (int) - id of the channel to join
        start        (int) - start of the message index

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
                    - start is greater than the total number of messages in the channel

        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns { messages, start, end }
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)
    data = data_store.get()

    # check the value of "start"
    all_messages = []
    for msg in data["messages"]:
        if msg["is_channel"] == True:
            if channel_id == msg["channel_id"]:
                all_messages = msg["all_msg"]

    if start > len(all_messages):
        raise InputError(
            description="start value is more than the total number of messages")

    if len(all_messages) == 0:
        return {"messages": [], "start": start, "end": -1}

    selected_messages = all_messages[start: (start + 50)]
    selected_messages.reverse()

    end = start + 50
    if len(selected_messages) <= 50:
        end = -1
    for each_message in selected_messages:
        for reacts in each_message["reacts"]:
            for reacted_user_id in reacts["u_ids"]:
                if auth_user_id == reacted_user_id:
                    reacts["is_this_user_reacted"] = True

    return {
        "messages": selected_messages,
        "start": start,
        "end": end,
    }


def channel_join_v2(token, channel_id):
    """
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.

    Arguments:
        token        (int) - token of the user
        channel_id   (int) - id of the channel to join

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
                    - the authorised user is already a member of the channel
        AccessError - channel_id refers to a channel that is private and
                    the authorised user is not already a channel member and is not a global owner
    Return Value:
        Returns nothing
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]
    auth_user_permission = 2

    # get the global permission of auth user
    auth_user_permission = check_auth_permission(auth_user_id)

    # search for a matching channel_id in the list of channels
    valid_channel_join = False
    for channel in channels:
        if channel_id == channel["channel_id"]:
            # found the matching channel
            valid_channel_join = True
            for member in channel["all_members"]:
                # check for valid join
                if auth_user_id == member:
                    raise InputError(
                        description="The authorised user is already a member of the channel")
                if not channel["is_public"] and auth_user_permission != 1:
                    raise AccessError(
                        description="This is a private channel and you don't have permission")

            # auth user joins channel
            channel["all_members"].append(auth_user_id)
            update_user_joined(token, auth_user_id, channel_id, -1)
            break

    # none of stored channels match with the argument
    if not valid_channel_join:
        raise InputError("Channel_id does not refer to a valid channel")

    # store data
    data_store.set(store)
    save_data()

    return {
    }


def channel_leave_v1(token, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a member of,
    remove them as a member of the channel. Their messages should remain in the channel.
    If the only channel owner leaves, the channel will remain.

    Arguments:
        token        (string) - token of the user
        channel_id   (int) - id of the channel to join

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns nothing
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]

    for channel in channels:
        # found the matching channel
        if channel_id == channel["channel_id"]:
            for member in channel["all_members"]:
                if auth_user_id == member:
                    channel["all_members"].remove(member)
            for owner in channel["owner_members"]:
                if auth_user_id == owner:
                    channel["owner_members"].remove(owner)
            update_user_joined(token, auth_user_id, channel_id, -2)

    # store data
    data_store.set(store)
    save_data()

    return {
    }


def channel_addowner_v1(token, channel_id, u_id):
    """
    Make user with user id u_id an owner of the channel.

    Arguments:
        token        (string) - token of the user
        channel_id   (int) - id of the channel to join
        u_id         (int) - List of user ids

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
                    - u_id does not refer to a valid user
                    - u_id refers to a user who is not a member of the channel
                    - u_id refers to a user who is already an owner of the channel
        AccessError - channel_id is valid and the authorised user
                      does not have owner permissions in the channel
                    - Occurs when token does not refer to a valid user

    Return Value:
        Returns nothing
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # check if u_id is valid and if u_id refer to a user already in the channel
    is_member = check_u_id_channel(u_id, channel_id)
    if not is_member:
        raise InputError(
            description="u_id refers to a user who is not a member of the channel")

    # get the global permission of auth user
    auth_user_permission = check_auth_permission(auth_user_id)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]

    is_owner = False
    for channel in channels:
        # found the matching channel
        if channel_id == channel["channel_id"]:
            for owner_member in channel["owner_members"]:
                if auth_user_id == owner_member:
                    is_owner = True
                if u_id == owner_member:
                    raise InputError(
                        description="u_id refers to a user who is already an owner of the channel")
            # add user as owner
            if is_owner == True or auth_user_permission == 1:
                channel["owner_members"].append(u_id)
            break

    if not is_owner and auth_user_permission == 2:
        raise AccessError(
            description="channel_id is valid but the authorised user does not have owner permissions in the channel")

    # store data
    data_store.set(store)
    save_data()

    return {
    }


def channel_removeowner_v1(token, channel_id, u_id):
    """
    Remove user with user id u_id as an owner of the channel.

    Arguments:
        token        (string) - token of the user
        channel_id   (int) - id of the channel to join
        u_id         (int) - List of user ids

    Exceptions:
        InputError  - channel_id does not refer to a valid channel
                    - u_id does not refer to a valid user
                    - u_id refers to a user who is not an owner of the channel
                    - u_id refers to a user who is already an owner of the channel
        AccessError - channel_id is valid and the authorised user
                      does not have owner permissions in the channel
                    - Occurs when token does not refer to a valid user

    Return Value:
        Returns nothing
    """

    # check the validity of token
    auth_user_id = token_validity(token)

    # check for validity of channel id and if auth user is in the channel
    check_auth_user_channel(auth_user_id, channel_id)

    # check if u_id is valid and if u_id refer to a user already in the channel
    is_member = check_u_id_channel(u_id, channel_id)
    if not is_member:
        raise InputError(
            description="u_id refers to a user who is not a member of the channel")

    # get the global permission of auth user
    auth_user_permission = check_auth_permission(auth_user_id)

    # get all info stored in data_store
    store = data_store.get()
    channels = store["channels"]

    auth_is_owner = False
    u_is_owner = False
    for channel in channels:
        # found the matching channel
        if channel_id == channel["channel_id"]:
            for owner_member in channel["owner_members"]:
                if auth_user_id == owner_member:
                    auth_is_owner = True
                if u_id == owner_member:
                    u_is_owner = True
            for owner_member in channel["owner_members"]:
                if u_id == owner_member:
                    if len(channel["owner_members"]) == 1:
                        raise InputError(
                            description="u_id refers to a user who is currently the only owner of the channel")
                    # remove from user owner list
                    if auth_is_owner == True or auth_user_permission == 1:
                        channel["owner_members"].remove(owner_member)
            break

    if not auth_is_owner and auth_user_permission == 2:
        raise AccessError(
            description="channel_id is valid but the authorised user does not have owner permissions in the channel")

    if not u_is_owner:
        raise InputError(
            description="u_id refers to a user who is not an owner of the channel")

    # store data
    data_store.set(store)
    save_data()

    return {
    }
