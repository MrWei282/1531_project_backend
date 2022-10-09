import re
from unicodedata import name
from src.data_store import data_store
from src.error import InputError, AccessError
from src.validity_check import token_validity
from src.user_info import collect_user_info
from src.persistence import save_data
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
from PIL import Image

def check_u_id_exist(u_id):
    '''
    function to check if the given u_id exists
    '''
    store = data_store.get()
    users = store["users"]

    is_valid = False
    for user in users:
        if user['u_id'] == u_id:
            is_valid = True
    if not is_valid:
        raise InputError(description = "u_id does not refer to a valid user")

    return is_valid


def check_valid_email(email):
    store = data_store.get()
    users = store["users"]

    # check for valid email format
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        raise InputError(description = "Email format not valid")

    # check for used email
    for user in users:
        if email == user["email"]:
            raise InputError(description = "Email already taken")

def check_name_length(name):
    '''
    This helper function is for checking the lenght of the given name
    '''
    if name is None or len(name) > 50 or len(name) < 1:
        raise InputError(description = "The given name has an invalid lenght.")

def set_user_name(token, name_first, name_last):

    #check the parameters and obtain u_id
    auth_user_id = token_validity(token)
    check_name_length(name_first)
    check_name_length(name_last)

    store = data_store.get()
    users = store["users"]

    for user in users:
        if user['u_id'] == auth_user_id:
            user['name_first'] = name_first
            user['name_last'] = name_last

    data_store.set(store)
    save_data()

def set_user_email(token, email):

    #check the parameters and obtain u_id
    auth_user_id = token_validity(token)
    check_valid_email(email)

    store = data_store.get()
    users = store["users"]

    for user in users:
        if user['u_id'] == auth_user_id:
            user['email'] = email

    data_store.set(store)
    save_data()

def info_profile(token, u_id):
    
    #check the parameters 
    token_validity(token)
    check_u_id_exist(u_id)

    store = data_store.get()
    users = store["users"]
    return_dict = {}
    for user in users:
        if user['u_id'] == u_id:
            return_dict = {
                "u_id" : user['u_id'],
                "email": user['email'],
                "name_first": user['name_first'],
                "name_last": user['name_last'],
                "handle_str": user['handle_str'],
                "profile_img_url": user['profile_img_url']
            }

    return {
        "user" : return_dict 
    }

def all_users(token):

    #check the parameters 
    token_validity(token)

    store = data_store.get()
    users = []
    for user in store["users"]:
        if not user["is_removed"]:
            user_data = {
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'u_id' : user['u_id'],
                'email' : user['email'],
                'handle_str' : user['handle_str']
            }
            users.append(user_data)

    return {
        'users' : users
    }

def set_user_handle(token, handle_str):

    #check the parameters and obtain u_id
    auth_user_id = token_validity(token)
    store = data_store.get()
    users = store["users"]

    if len(handle_str) > 20 or len(handle_str) < 3:
        raise InputError(description = "Handle_str has an invalid lenght")
    
    is_repeated = False
    for user in users:
        if user['handle_str'] == handle_str:
            is_repeated = True
    if is_repeated:
        raise InputError(description = "the handle is already used by another user")

    if not handle_str.isalnum():
        raise InputError(description = "Handle has to be alphanumeric")

    
    for user in users:
        if user['u_id'] == auth_user_id:
            user['handle_str'] = handle_str

    data_store.set(store)
    save_data()

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    """_summary_

    Args:
        token (_type_): _description_
        img_url (_type_): _description_
        x_start (_type_): _description_
        y_start (_type_): _description_
        x_end (_type_): _description_
        y_end (_type_): _description_
    """
    store = data_store.get()
    auth_user_id = token_validity(token)
    file_name = token
    urlretrieve(img_url, file_name)
    img = Image.open(file_name)
    img.crop((x_start, y_start, x_end, y_end))
    users = store['users']
    for user in users:
        if user['u_id'] == auth_user_id:
            user["profile_img_url"] = img_url
    data_store.set(store)
    save_data()