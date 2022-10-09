'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

data_structure:
store = {
    "users": [
        {
            "u_id": int(auth_user_id),
            "email": email,
            "password": password,
            "name_first": name_first,
            "name_last": name_last,
            "handle_str": handle,
            "permission_id": permission_id,
            "session_id_list": [session_id],
            "joined_channels": [channel_ids],
            "joined_dms": [dm_ids],
            "is_removed": bool(user_removed)
            "profile_img_url": str(url)
            "user_stats": {
                "channels_joined": [
                    {
                    "num_channels_joined": int(num_channels_joined),
                    "time_stamp": int(time_stamp),
                    }
                ], 
                "dms_joined": [
                    {
                    "num_dms_joined": int(num_dms_joined),
                    "time_stamp": int(time_stamp),
                    }
                ], 
                "messages_sent": [
                    {
                    "num_messages_sent": int(num_messages_sent), 
                    "time_stamp": int(time_stamp),
                    }
                ], 
                "involvement_rate": sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_channels, num_dms, num_msgs)
            }
            "is_removed": bool(user_removed)
            "notifications": [
                {
                "channel_id": channel_id,
                "dm_id": dm_id,
                "notification_message": notification_message,
                }
            ]
        },
    ],
    "channels": [
        {
            "name": name,
            "is_public": bool(is_public),
            "channel_id": int(channel_id),
            "owner_members": [owner_id],
            "all_members": [member_id],
            "message_id_list": [message_id],
            "is_standup_active": bool(is_standup_active),
            "standup_time_finish ": standup_time_finish 
            "standup_msg": [buffer_msg]
        },
    ],
    'messages': [
        {
            "is_channel": bool(channel_msg_list)
            "is_dm": bool(dm_msg_list)
            "channel_id": channel_id or "dm_id": dm_id,
            "all_msg": [
                {
                "message_id": utc_timestamp,
                "u_id": u_id,
                "message": message, 
                "time_sent: utc_timestamp,
                "is_pined": bool(message)
                "reacts":[
                    {
                        "react_id": react_id,
                        "u_ids": [reacted_user_id],
                        "is_this_user_reacted": bool(is_this_user_reacted)
                    }
                ]
                }
            ]
        }
    ]
    'dms':[
        'dm_id': len(dms) + 1,(int)
        'name': generate_dm_name(all_members),(str)
        'owner': creator_u_id,(int)
        'all_members': all_members,[member_ids]
        'message_id_list': [message_id],
    ],
    'workspace_stats': {'channels_exist': [],
                        'dms_exist': [],
                        'messages_exist': [],
                        'utilization_rate'
                        }
}
'''

# YOU SHOULD MODIFY THIS OBJECT BELOW
from datetime import timezone
import datetime

dt = datetime.datetime.now(timezone.utc)
utc_time = dt.replace(tzinfo=timezone.utc)
time_stamp = utc_time.timestamp()

initial_object = {
    "users": [],
    "channels": [],
    "messages": [],
    "dms": [],
    'workspace_stats': {'channels_exist': [{
                            "num_channels_exist": 0,
                            "time_stamp": time_stamp
                        }],
                        'dms_exist': [{
                            "num_dms_exist": 0,
                            "time_stamp": time_stamp
                        }],
                        'messages_exist': [{
                            "num_messages_exist": 0,
                            "time_stamp": time_stamp
                        }],
                        'utilization_rate': 0,
                        }
    }
# YOU SHOULD MODIFY THIS OBJECT ABOVE

# YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH


class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError("store must be of type dictionary")
        self.__store = store


print("Loading Datastore...")

global data_store
data_store = Datastore()
