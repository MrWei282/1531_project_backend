from src.data_store import data_store
from src.error import InputError, AccessError
from src.validity_check import token_validity
from src.persistence import save_data
from src.user_info import update_user_joined

def admin_user_remove_v1(token, u_id):
    # checking valid token
    auth_user_id = token_validity(token)
    
    # get data
    store = data_store.get()
    users = store["users"]
    
    is_valid_user = False
    is_global_owner = False
    num_global = 0
    for user in users:
        if u_id == user["u_id"]:
            is_valid_user = True
        if auth_user_id == user["u_id"]:
            if user["permission_id"] == 1:
                is_global_owner = True
        if user["permission_id"] == 1:
            num_global = num_global + 1

    if not is_valid_user:
        raise InputError(description="u_id does not refer to a valid user")

    if not is_global_owner:
        raise AccessError(description="the authorised user is not a global owner")
    
    if num_global <= 1 and auth_user_id == u_id:
        raise InputError(description="u_id refers to a user who is the "+ 
                         "only global owner and they are being demoted to a user")

    for user in users:
        if u_id == user["u_id"]:
            for channel_id in user["joined_channels"]:
                channels = store["channels"]
                for channel in channels:
                    # find the correct channel
                    if channel_id == channel["channel_id"]:
                        for member in channel["all_members"]:
                            if u_id == member:
                                channel["all_members"].remove(member)
                        for owner in channel["owner_members"]:
                            if u_id == owner:
                                channel["owner_members"].remove(owner)
                user["joined_channels"] = []

            for dm_id in user["joined_dms"]:
                dms = store["dms"]
                for dm in dms:
                    # find the correct dm
                    if  dm_id == dm['dm_id']:
                        # find the user inside the list of members
                        for dm_member in dm['all_members']:
                            if dm_member == u_id:
                                dm['all_members'].remove(dm_member)
                user["joined_dms"] = []

            user["name_first"] = "Removed"
            user["name_last"] = "user"
            user["email"] = ""
            user["handle_str"] = ""
            user["permission_id"] = 2
            
            for msg in store["messages"]:
                for msg_info in msg["all_msg"]:
                    if msg_info["u_id"] == u_id:
                        msg_info["message"] = "Removed user"
            
            user["is_removed"] = True

    data_store.set(store)
    save_data()

    return {
    }


def admin_userpermission_change_v1(token, u_id, permission_id):
    # checking valid token
    auth_user_id = token_validity(token)

    if (permission_id != 1 and permission_id != 2):
        raise InputError(description="permission_id is invalid")
    
    # get data
    store = data_store.get()
    users = store["users"]
    
    is_valid_user = False
    is_global_owner = False
    num_global = 0
    for user in users:
        if u_id == user["u_id"]:
            is_valid_user = True
            if user["permission_id"] == permission_id:
                raise InputError(description="the user already has the permissions level of permission_id")
        if auth_user_id == user["u_id"]:
            if user["permission_id"] == 1:
                is_global_owner = True
        if user["permission_id"] == 1:
            num_global = num_global + 1

    if not is_global_owner:
        raise AccessError(description="the authorised user is not a global owner")

    if not is_valid_user:
        raise InputError(description="u_id does not refer to a valid user")
    
    if num_global <= 1 and permission_id == 2 and auth_user_id == u_id:
        raise InputError(description="u_id refers to a user who is the "+ 
                         "only global owner and they are being demoted to a user")
    
    for user in users:
        if u_id == user["u_id"]:
            user["permission_id"] = permission_id
    
    data_store.set(store)
    save_data()
    
    return {
    }