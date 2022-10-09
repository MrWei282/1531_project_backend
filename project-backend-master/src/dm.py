from src.data_store import data_store
from src.error import InputError, AccessError
from src.validity_check import token_validity
from src.persistence import save_data
from src.user_info import update_user_joined, update_ch_dm_workspace
from src.other import *

from datetime import timezone
import datetime


def dm_create_v1(token, u_ids):
    '''
    u_ids contains the user(s) that this DM is directed to,
    and will not include the creator. The creator is the owner of the DM.
    name should be automatically generated based on the users that are in this DM.
    The name should be an alphabetically-sorted, comma-and-space-separated list of user handles,
    e.g. 'ahandle1, bhandle2, chandle3'.

    Arguments:
        token (string)    - token of user
        u_ids (List of user ids)    - list of all the members
    Exceptions:
        InputError - Occurs when a u_id does not refer to a valid member
        AccessError - Occurs when token is invalid
    Return Value:
        Returns {dm_id} on success
    '''
    # checking valid token
    creator_u_id = token_validity(token)

    # Define list of all members in new dm
    all_members = [creator_u_id]

    # Verifies that the users would be added in dm exist in the data store and add to the all member list of the new dm, raises an InputError
    for u_id in u_ids:
        if not verify_user_id(u_id):
            raise InputError(description="User not exist.")
        all_members.append(u_id)


# dm directroy as follow:
#     'dm_id'        :   integer type - assigned sequentially
#     'name'         :   string type - alphabetically-sorted, comma-and-space separated list of user handles, e.g. ahandle1, bhandle2, chandle3
#     'owner'        :   user ids - creator made an owner
#     'all_members'  :   list of user ids - creator and added members made in all members
#     'messages'     :   list of dictionaries for message details i.e.
#                         { message_id, u_id, message }
    # get data
    store = data_store.get()
    users = store["users"]
    dms = store['dms']

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_sent = utc_time.timestamp()
    dm_id = int(time_sent * 1000000)
    
    new_dm = {
        'dm_id': dm_id,
        'name': generate_dm_name(all_members),
        'owner': creator_u_id,
        'all_members': all_members,
        'message_id_list': [],
    }
    dms.append(new_dm)
    
    init_msg = {
        "dm_id": dm_id,
        "is_channel": False,
        "is_dm": True,
        "all_msg": []
    }
    store["messages"].append(init_msg)

    for user in users:
        if creator_u_id == user["u_id"]:
            auth_str = user["handle_str"]
            break

    update_user_joined(token, creator_u_id, -1, dm_id)
    update_ch_dm_workspace(False)
    for u_id in u_ids:
        update_user_joined(token, u_id, -1, dm_id)
        for user in users:
            if u_id == user["u_id"]:
                dm_name = new_dm["name"]
                notification_info = {
                    "channel_id": -1,
                    "dm_id": dm_id,
                    "notification_message": f"{auth_str} added you to {dm_name}"
                }
                user["notifications"].append(notification_info)
                break
    
    data_store.set(store)
    save_data()

    return {
        'dm_id': dm_id,
    }

def user_data(dm_members, store_users):
    '''
    Get the details of all users in the given dm
    '''
    users_list = []
    for user in store_users:
        for member in dm_members:
            if member == user['u_id']:
                users_list.append({
                    'u_id' : user['u_id'],
                    'email': user['email'],
                    'name_first': user['name_first'],
                    'name_last': user['name_last'],
                    'handle_str': user['handle_str'],
                    #'profile_img_url': user['profile_img_url']
                })

    return users_list


def dm_details(token, dm_id):
    """
    Given an dm_id, returns the basic details about the given dm

    Args:
        token (str): token of user
        dm_id (int): dm's id number

    Raises:
        AccessError: dm_id does not refer to a valid id
        InputError: dm_id is valid but user is not a member of the DM

    Returns:
        name: name of the dm
        members: list of directories where each directory is an user
    """

    # get list of dms from the data base
    store = data_store.get()
    dms = store["dms"]

    # check the token
    u_id = token_validity(token)

    return_details = {}
    dm_valid = False
    id_member = False
    for dm in dms:
        # find the correct dm
        if dm['dm_id'] == dm_id:
            dm_valid = True
            # find the user inside the list of members
            for user in dm['all_members']:
                if user == u_id:
                    id_member = True
                    return_details = {
                        'name': dm['name'],
                        'members': user_data(dm['all_members'], store['users'])
                    }

    if dm_valid and not id_member:
        raise AccessError(description="dm_id is valid and \
            the authorised user is not a member of the DM")
    if not dm_valid:
        raise InputError(description="dm_id does not refer to a valid DM")

    return return_details

def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is a member of.

    Arguments:
        token(string) - Users id
    Exceptions:
        NA
    Return Value:
        Returns {dms} on success
    '''
  
    # check the validity of token
    auth_user_id = token_validity(token)

    # get all info stored in data_store
    store = data_store.get()
    dm_store = store['dms']
    dms = []

    for dm in dm_store:
        if auth_user_id in dm['all_members']:
            dms.append({'dm_id': dm['dm_id'], 'name': dm['name']})

    return{
        'dms': dms
    }

def dm_remove_v1(token, dm_id):
    '''
    Given a dm with ID dm_id that the authorised user is a member of,
    removing an existing dm, so all members are no longer in the dm. This can only
    done by the original creator of the dm.
        Arguments:
            token (str)             - authorised user id of the user who is a creator of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.
        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.
            AccessError - Occurs when dm_id is valid and the authorised user is
                          not the creator of the dm.
        Return Value:
            Returns { } on successful completion.
    '''
    # get all info stored in data_store
    store = data_store.get()

    dm_store = store['dms']
    # check for valid dm_id

    # Removes DM if it can find it
    user_id = token_validity(token)
    is_creator = False
    creator_in_dm = False
    dm_valid = False
    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            dm_valid = True
            # Check if authorised user is an all_members of DM
            if user_id == dm['owner']:
                for member_id in dm["all_members"]:
                    if member_id == user_id:
                        creator_in_dm = True
                if creator_in_dm == True:
                    is_creator = True
                    for member_id in dm["all_members"]:
                        update_user_joined(token, member_id, -2, dm_id)
                    dm_store.remove(dm)
                    update_ch_dm_workspace(False)
                else:
                    raise AccessError(description="dm_id is valid and the authorised" +
                                      "user is no longer in the DM")

    if dm_valid == False:
        raise InputError(description="Dm_id does not refer to a valid DM")
    if is_creator == False:
        raise AccessError(description="User is not the original DM creator")
    
    data_store.set(store)
    save_data()
    
    return {}

def dm_leave_v1(token, dm_id):
    """
    Given an dm_id and token, the user leaves the given dm

    Args:
        token (str): token of user
        dm_id (int): dm's id number

    Raises:
        AccessError: dm_id does not refer to a valid id
        InputError: dm_id is valid but user is not a member of the DM

    Returns:
        {} on success
    """
    # get all info stored in data_store
    store = data_store.get()

    dms = store['dms']
    # check for valid dm_id

    u_id = token_validity(token)

    dm_valid = False
    id_member = False
    for dm in dms:
        # find the correct dm
        if dm['dm_id'] == dm_id:
            dm_valid = True
            # find the user inside the list of members
            for user in dm['all_members']:
                if user == u_id:
                    id_member = True
                    dm['all_members'].remove(user)
                    update_user_joined(token, u_id, -2, dm_id)

    if dm_valid and not id_member:
        raise AccessError(description="dm_id is valid and \
            the authorised user is not a member of the DM")
    if not dm_valid:
        raise InputError(description="dm_id does not refer to a valid DM")
    
    data_store.set(store)
    save_data()

    return {}

def dm_messages_v1(token, dm_id, start):
    '''
    Given a dm with ID dm_id that the authorised user is a member of,
    removing an existing dm, so all members are no longer in the dm. This can only
    done by the original creator of the dm.
        Arguments:
            token (str)             - authorised user id of the user who is a creator of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.
        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.
            AccessError - Occurs when dm_id is valid and the authorised user is
                          not the creator of the dm.
        Return Value:
            Returns {message, start, end } on successful completion.
    '''
    auth_user_id = token_validity(token)

    # Get data
    store = data_store.get()
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
        raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM")

    data = data_store.get()

    # check the value of "start"
    all_messages = []
    for msg in data["messages"]:
        if msg["is_dm"] == True:
            if dm_id == msg["dm_id"]:
                all_messages = msg["all_msg"]

    if start > len(all_messages):
        raise InputError(description = "start value is more than the total number of messages")

    if len(all_messages) == 0:
        return {"messages": [], "start": start, "end": -1}

    selected_messages = all_messages[start : (start + 50)]
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
