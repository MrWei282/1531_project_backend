"""This script contains functions to generate and decode jwt"""

from distutils.log import error
import jwt

from src.error import AccessError

SESSION_TRACKER = 0
SIGNITURE = 'W17B_DINGO'

def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER

def reset_session():
    global SESSION_TRACKER
    SESSION_TRACKER = 0

def generate_jwt(auth_user_id, session_id):
    """Generates a JWT using the global SECRET

    Args:
        username ([string]): The username
        session_id ([string], optional): The session id, if none is provided will
                                         generate a new one. Defaults to None.

    Returns:
        string: A JWT encoded string
    """

    return jwt.encode({'auth_user_id': auth_user_id, 'session_id': session_id}, SIGNITURE, algorithm='HS256')

def decode_jwt(encoded_jwt):
    """Decodes a JWT string into an object of the data

    Args:
        encoded_jwt ([string]): The encoded JWT as a string

    Returns:
        Object: An object storing the body of the JWT encoded string
    """

    decorded_jwt = {
        'auth_user_id': 0, 
        'session_id': 0
    }
    
    jwt_valid = True
    
    try: 
        decorded_jwt = jwt.decode(encoded_jwt, SIGNITURE, algorithms=['HS256'])
    except:
        jwt_valid = False
    
    if not jwt_valid:
        raise AccessError(description = "token is not correctly formatted")
    return decorded_jwt
