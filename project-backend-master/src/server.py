import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config

from src.persistence import load_data
from src.other import clear_v1, notification_v1
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_join_v2
from src.channel import channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1, message_react_v1, message_unreact_v1
from src.message import message_share_v1, message_sendlater_v1, message_sendlaterdm_v1, message_pin_v1, message_unpin_v1
from src.user_profile import set_user_handle, set_user_name, set_user_email, info_profile, all_users, user_profile_uploadphoto_v1
from src.dm import dm_create_v1, dm_details , dm_list_v1, dm_remove_v1, dm_messages_v1, dm_leave_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.user_info import user_stats_v1, users_stats_v1
from src.search import get_query
from src.password import send_email_request, reset_pass
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example


@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/clear/v1", methods=["DELETE"])
def clear():
    clear_v1()
    return dumps({})


@APP.route("/auth/login/v2", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data['password']

    user = auth_login_v2(email, password)
    token = str(user['token'])
    auth_user_id = int(user['auth_user_id'])

    return dumps({
        'token': token,
        'auth_user_id': auth_user_id
    })


@APP.route("/auth/register/v2", methods=["POST"])
def register():
    data = request.get_json()
    email = str(data['email'])
    password = str(data['password'])
    name_first = str(data['name_first'])
    name_last = str(data['name_last'])

    user = auth_register_v2(email, password, name_first, name_last)
    token = str(user['token'])
    auth_user_id = int(user['auth_user_id'])

    return dumps({
        'token': token,
        'auth_user_id': auth_user_id
    })


@APP.route("/auth/logout/v1", methods=["POST"])
def logout():
    data = request.get_json()
    token = str(data['token'])

    auth_logout_v1(token)

    return dumps({
    })


@APP.route("/channels/create/v2", methods=["POST"])
def create():
    data = request.get_json()
    token = str(data['token'])
    name = str(data['name'])
    is_public = bool(data['is_public'])

    channel_id = int(channels_create_v2(token, name, is_public)['channel_id'])
    return dumps({
        'channel_id': channel_id
    })


@APP.route("/channels/list/v2", methods=["GET"])
def list():
    token = str(request.args.get('token'))
    channels = channels_list_v2(token)['channels']

    return dumps({
        "channels": channels,
    })


@APP.route("/channels/listall/v2", methods=["GET"])
def listall():
    token = str(request.args.get('token'))
    channels = channels_listall_v2(token)['channels']

    return dumps({
        "channels": channels,
    })


@APP.route("/channel/invite/v2", methods=["POST"])
def invite():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])

    channel_invite_v2(token, channel_id, u_id)

    return dumps({
    })


@APP.route("/channel/details/v2", methods=["GET"])
def details():
    token = str(request.args.get('token'))
    channel_id = int(request.args.get('channel_id'))

    channel_detail = channel_details_v2(token, channel_id)
    name = str(channel_detail['name'])
    is_public = bool(channel_detail['is_public'])
    owner_members = channel_detail['owner_members']
    all_members = channel_detail['all_members']

    return dumps({
        "name": name,
        "is_public": is_public,
        "owner_members": owner_members,
        "all_members": all_members
    })


@APP.route("/channel/messages/v2", methods=["GET"])
def message():
    token = str(request.args.get('token'))
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    channel_message = channel_messages_v2(token, channel_id, start)
    messages = channel_message['messages']
    start = int(channel_message['start'])
    end = int(channel_message['end'])

    return dumps({
        "messages": messages,
        "start": start,
        "end": end
    })


@APP.route("/channel/join/v2", methods=["POST"])
def join():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])

    channel_join_v2(token, channel_id)

    return dumps({
    })


@APP.route("/channel/leave/v1", methods=["POST"])
def leave():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])

    channel_leave_v1(token, channel_id)

    return dumps({
    })


@APP.route("/channel/addowner/v1", methods=["POST"])
def addowner():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])

    channel_addowner_v1(token, channel_id, u_id)

    return dumps({
    })


@APP.route("/channel/removeowner/v1", methods=["POST"])
def removeowner():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])

    channel_removeowner_v1(token, channel_id, u_id)

    return dumps({
    })


@APP.route("/message/send/v1", methods=["POST"])
def message_send():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    message = str(data['message'])

    message_id = int(message_send_v1(token, channel_id, message)["message_id"])

    return dumps({
        "message_id": message_id
    })


@APP.route("/message/edit/v1", methods=["PUT"])
def message_edit():
    data = request.get_json()
    token = str(data['token'])
    message_id = int(data['message_id'])
    message = str(data['message'])

    message_edit_v1(token, message_id, message)

    return dumps({
    })


@APP.route("/message/remove/v1", methods=["DELETE"])
def message_remove():
    data = request.get_json()
    token = str(data['token'])
    message_id = int(data['message_id'])

    message_remove_v1(token, message_id)

    return dumps({
    })


@APP.route("/user/profile/setname/v1", methods=["PUT"])
def setname():
    data = request.get_json()

    token = data['token']
    name_first = data['name_first']
    name_last = data['name_last']
    set_user_name(token, name_first, name_last)

    return dumps({
    })


@APP.route("/user/profile/setemail/v1", methods=["PUT"])
def setemail():
    data = request.get_json()

    token = data['token']
    email = data['email']
    set_user_email(token, email)

    return dumps({
    })


@APP.route("/user/profile/v1", methods=["GET"])
def info_profile_():
    token = str(request.args.get("token"))
    u_id = int(request.args.get("u_id"))
    profile_data = info_profile(token, u_id)

    return dumps({
        'user': profile_data['user']
    })


@APP.route("/users/all/v1", methods=["GET"])
def list_all_users():
    token = str(request.args.get("token"))

    return dumps(
        all_users(token)
    )


@APP.route("/user/profile/sethandle/v1", methods=["PUT"])
def sethandle():
    data = request.get_json()

    token = data['token']
    future_handle = data['handle_str']
    set_user_handle(token, future_handle)

    return dumps({})

@APP.route("/auth/passwordreset/request/v1", methods=["POST"])
def email_request():
    data = request.get_json()
    send_email_request(str(data['email']))

    return dumps({
    })

@APP.route("/dm/create/v1", methods=["POST"])
def dm_create():
    data = request.get_json()
    token = str(data['token'])
    u_ids = data['u_ids']

    dm_id = int(dm_create_v1(token, u_ids)["dm_id"])

    return dumps({
        "dm_id": dm_id,
    })


@APP.route("/dm/list/v1", methods=["GET"])
def dm_list():
    token = str(request.args.get('token'))
    dms = dm_list_v1(token)['dms']

    return dumps({
        "dms": dms,
    })


@APP.route("/dm/details/v1", methods=["GET"])
def dm_details_v1():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    return dumps(
        dm_details(token, dm_id)
    )


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']

    dm_remove_v1(token, dm_id)

    return dumps({})


@APP.route("/dm/leave/v1", methods=["POST"])
def dm_leave():
    data = request.get_json()
    dm_leave_v1(data['token'], data['dm_id'])

    return dumps({})


@APP.route("/dm/messages/v1", methods=["GET"])
def dm_message():
    token = str(request.args.get('token'))
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))

    dm_message = dm_messages_v1(token, dm_id, start)
    messages = dm_message['messages']
    start = int(dm_message['start'])
    end = int(dm_message['end'])

    return dumps({
        "messages": messages,
        "start": start,
        "end": end
    })


@APP.route("/message/senddm/v1", methods=["POST"])
def message_senddm():
    data = request.get_json()
    token = str(data['token'])
    dm_id = int(data['dm_id'])
    message  = str(data['message'])
    
    message_id = int(message_senddm_v1(token, dm_id, message)["message_id"])

    return dumps({
        "message_id": message_id
    })

@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])
def reset_the_pass():
    data = request.get_json()
    code = str(data['reset_code'])
    new = str(data['new_password'])
    reset_pass(code, new)
    return dumps({
    })


@APP.route("/search/v1", methods=["GET"])
def search_v1():
    query = str(request.args.get('query_str'))
    token = str(request.args.get('token'))
    return dumps({
        'messages': get_query(token, query)
    })


@APP.route("/admin/user/remove/v1", methods=["DELETE"])
def admin_remove():
    data = request.get_json()
    token = str(data['token'])
    u_id = int(data['u_id'])

    admin_user_remove_v1(token, u_id)

    return dumps({
    })


@APP.route("/admin/userpermission/change/v1", methods=["POST"])
def admin_permission():
    data = request.get_json()
    token = str(data['token'])
    u_id = int(data['u_id'])
    permission_id = int(data['permission_id'])

    admin_userpermission_change_v1(token, u_id, permission_id)

    return dumps({
    })


@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    '''
    Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future
    Arguments:
        token (string)      - Token of user sending the message
        channel_id (int)    - Unique ID of channel
        message (string)    - Message user is sending
        time_sent (int)     - The time the user message is executed
    Exceptions:
        Input Error:
        - channel_id does not refer to a valid channel
        - length of message is less than 1 or over 1000 characters
        - time_sent is a time in the past
        Access Error:
        - channel_id is valid and the authorised user is not a member of the channel they are trying to post to
    Return Value:
        { message_id }
    '''
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    message = str(data['message'])
    time_sent = data['time_sent']

    message_id = int(message_sendlater_v1(
        token, channel_id, message, time_sent)["message_id"])

    return dumps({
        "message_id": message_id
    })


@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm():
    '''
    Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future
    Arguments:
        token (string)      - Token of user sending the message
        channel_id (int)    - Unique ID of channel
        message (string)    - Message user is sending
        time_sent (int)     - The time the user message is executed
    Exceptions:
        Input Error:
        - channel_id does not refer to a valid channel
        - length of message is less than 1 or over 1000 characters
        - time_sent is a time in the past
        Access Error:
        - channel_id is valid and the authorised user is not a member of the channel they are trying to post to
    Return Value:
        { message_id }
    '''
    data = request.get_json()
    token = str(data['token'])
    dm_id = int(data['dm_id'])
    message = str(data['message'])
    time_sent = data['time_sent']

    message_id = int(message_sendlaterdm_v1(
        token, dm_id, message, time_sent)["message_id"])

    return dumps({
        "message_id": message_id
    })

@APP.route("/message/react/v1", methods=["POST"])
def react():
    data = request.get_json()
    token = str(data['token'])
    message_id = int(data['message_id'])
    react_id = int(data['react_id'])

    message_react_v1(token, message_id, react_id)

    return dumps({
    })

@APP.route("/message/unreact/v1", methods=["POST"])
def unreact():
    data = request.get_json()
    token = str(data['token'])
    message_id = int(data['message_id'])
    react_id = int(data['react_id'])

    message_unreact_v1(token, message_id, react_id)

    return dumps({
    })

@APP.route("/message/share/v1", methods=["POST"])
def message_share():
    data = request.get_json()
    token = str(data['token'])
    og_message_id = int(data['og_message_id'])
    message = str(data['message'])
    channel_id = int(data['channel_id'])
    dm_id = int(data['dm_id'])
    
    shared_message_id = message_share_v1(token, og_message_id, message, channel_id, dm_id)
    
    return dumps({
        "shared_message_id": shared_message_id
    })
    
@APP.route("/user/profile/uploadphoto/v1", methods=["POST"])
def user_profile_uploadphoto():
    data = request.get_json()
    token = str(data['token'])
    img_url = str(data["img_url"])
    x_start = int(data['x_start'])
    x_end = int(data['x_end'])
    y_start = int(data['y_start'])
    y_end = int(data['y_end'])
    
    user_profile_uploadphoto_v1(token, img_url, x_start, x_end, y_start, y_end)

    return dumps({})

@APP.route("/notifications/get/v1", methods=["GET"])
def notification():
    token = str(request.args.get('token'))
    notifications = notification_v1(token)

    return dumps({
        "notifications": notifications
    })

@APP.route("/standup/start/v1", methods=["POST"])
def standup_start():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    length = int(data['length'])

    time_finish = standup_start_v1(token, channel_id, length)

    return dumps ({
        "time_finish": time_finish
    })

@APP.route("/standup/active/v1", methods=["GET"])
def standup_active():
    token = str(request.args.get('token'))
    channel_id  = int(request.args.get('channel_id'))
    
    standup_active_info = standup_active_v1(token, channel_id)

    return dumps({
        "is_active": bool(standup_active_info['is_active']),
        "time_finish": standup_active_info['time_finish']
    })

@APP.route("/standup/send/v1", methods=["POST"])
def standup_send():
    data = request.get_json()
    token = str(data['token'])
    channel_id = int(data['channel_id'])
    message = str(data['message'])

    standup_send_v1(token, channel_id, message)

    return dumps ({
    })

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    data = request.get_json()

    token = data["token"]
    message_id = data["message_id"]
    message_pin_v1(token, message_id)
    return dumps({
    })
    
@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    data = request.get_json()

    token = data["token"]
    message_id = data["message_id"]
    message_unpin_v1(token, message_id)
    return dumps({
    })

@APP.route("/user/stats/v1", methods=["GET"])
def user_stats():
    token = str(request.args.get('token'))

    return dumps({"user_stats": user_stats_v1(token)})

@APP.route('/users/stats/v1', methods=['GET'])
def get_users_stats():
    token = str(request.args.get('token'))

    return dumps({"workspace_stats": users_stats_v1(token)})

# NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    load_data()
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
