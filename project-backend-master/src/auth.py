"""
This script contains two functions that allow user to login based on stored data, register user, and logout
"""

import re
import hashlib

from src.data_store import data_store
from src.error import InputError, AccessError
from src.persistence import save_data
from src.generate_token import generate_new_session_id, generate_jwt, decode_jwt
from datetime import timezone
import datetime

def auth_login_v2(email, password):
    """
    Given a registered user's email and password, returns their "auth_user_id" value.

    Arguments:
        email    (string) - email of the user
        password (string) - password of the user

    Exceptions:
        InputError  - Occurs when email entered is not registered
                    - Occurs when is not correct

    Return Value:
        Returns a dictionary containing auth_user_id
    """

    # get all info stored in data_store
    store = data_store.get()
    users = store["users"]

    # check for user info with given email and password
    email_registered = False
    for user in users:
        if email == user["email"]:
            email_registered = True
            auth_user_id = user["u_id"]
            # check for correct password
            if hashlib.sha256(password.encode()).hexdigest() != user["password"]:
                raise InputError(description = "Password incorrect, please enter again")
            # generate session_id
            session_id = generate_new_session_id()
            user["session_id_list"].append(session_id)

    # check for registered email
    if not email_registered:
        raise InputError(description = "Email not registered")
    
    # generate user token with auth_user_id and session_id
    user_jwt = generate_jwt(auth_user_id, session_id)
    
    # store data
    data_store.set(store)
    save_data()

    return {
        "token": user_jwt,
        "auth_user_id": int(auth_user_id),
    }

def auth_register_v2(email, password, name_first, name_last):
    """
    Given a user's first and last name, email address, and password,
    create a new account for them and return a new "auth_user_id".

    Arguments:
        email      (string) - email of the user
        password   (string) - password of the user
        name_first (string) - first name of the user
        name_last  (string) - last name of the user

    Exceptions:
        InputError  - Occurs when email entered is not in valid email format
                    - Occurs when email address is already being registered
                    - Occurs when length of password is less than 6 characters
                    - Occurs when length of name_first is not between 1 and 50 characters inclusive
                    - Occurs when length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        Returns a dictionary containing auth_user_id
    """

    # get all info stored in data_store
    store = data_store.get()
    users = store["users"]

    # create handle
    handle = name_first + name_last
    handle = re.sub(r"\W+", '', handle)
    handle = handle.lower()
    handle = handle[:20]

    # check for valid email format
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        raise InputError(description = "Email format not valid")

    # check for used email
    for user in users:
        if email == user["email"]:
            raise InputError(description = "Email already taken")

    # check for valid password
    if len(password) < 6:
        raise InputError(description = "Password need to be longer than 6")

    # check for valid name
    if (len(name_first) < 1 or len(name_first) > 50):
        raise InputError(description = "First name need to be between 1 and 50")
    if (len(name_last) < 1 or len(name_last) > 50):
        raise InputError(description = "Last name need to be between 1 and 50")

    # check and update handle for duplicate name
    idx = -1
    for user in users:
        if handle == user["handle_str"]:
            idx += 1
            print(idx)
            handle = re.sub(r"\d+", "", handle)
            handle += (str(idx))

    # generate auth_user_id
    auth_user_id = len(store["users"]) + 1

    # generate session_id
    session_id = generate_new_session_id()

    # hash the password
    password = hashlib.sha256(password.encode()).hexdigest()

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    time_stamp = utc_time.timestamp()

    # store data
    user_info = {
        "u_id": int(auth_user_id),
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last,
        "handle_str": handle,
        "permission_id": 2,
        "session_id_list": [session_id],
        "joined_channels": [],
        "joined_dms": [],
        "is_removed": False,
        "profile_img_url": "",
        "user_stats": {
            "channels_joined": [{
                "num_channels_joined": 0,
                "time_stamp": int(time_stamp),
                }],
            "dms_joined": [{
                "num_dms_joined": 0,
                "time_stamp": int(time_stamp),
                }],
            "messages_sent": [{
                "num_messages_sent": 0, 
                "time_stamp": int(time_stamp),
                }],
            "involvement_rate": 0,
        },
        "notifications": [],
    }
    
    # The first user that sign up is a global owner
    if len(users) == 0:
        user_info["permission_id"] = 1    
    
    # generate user token with auth_user_id and session_id
    user_jwt = generate_jwt(auth_user_id, session_id)
    
    # store data
    users.append(user_info)
    data_store.set(store)
    save_data()

    return {
        "token": user_jwt,
        "auth_user_id": int(auth_user_id),
    }

def auth_logout_v1(token):
    """
    user logout

    Args:
        token (_type_): _description_

    Raises:
        AccessError: _description_
        AccessError: _description_

    Returns:
        _type_: _description_
    """
    # check the validity of token
    store = data_store.get()
    users = store["users"]

    valid_token = False
    token_info = decode_jwt(token)

    for user in users:
        if token_info["auth_user_id"] == user["u_id"]:
            # user has an empty session_id_list
            if not user["session_id_list"]:
                raise AccessError(description = "user has not login")
            
            if token_info["session_id"] == user["session_id_list"][-1]:
                valid_token = True
                # initialise user's session_id_list
                user["session_id_list"] = []
                return {
                }

    if not valid_token:
        raise AccessError(description = "token is not valid")

    data_store.set(store)
    save_data()

    return {
    }
