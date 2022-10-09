from src.dm     import dm_list_v1
from src.channels import channels_listall_v2
from src.data_store import data_store
from src.validity_check import token_validity
from src.error import InputError

def get_query(token, query):
    """
    This functions is to search queries inside messages

    Args:
        u_id (int): u_id to identify the user
        query (str): query that we are searching for

    Raises:
        InputError: length of query_str is less than 1 or over 1000 characters

    Returns:
        messages: list of dictionaries where each dictionary is type message
    """
    
    result = []
    token_validity(token)
    store = data_store.get()
    size = len(query)
    if size < 1 or size > 1000:
        raise InputError(description="Invalid query size")

    joined_channels = channels_listall_v2(token)['channels']
    joined_dms = dm_list_v1(token)['dms']

    for message in store['messages']:
        #when the message is in a channel
        if message['is_channel'] is True:
            member = False
            for channel in joined_channels:
                if channel['channel_id'] == message['channel_id']:
                    member = True
            if not member:
                continue
            for msg in message['all_msg']:
                if query in msg['message']:
                    result.append(msg.copy())

        #when the message is in a dm
        else:
            member = False
            for dm in joined_dms:
                if dm['dm_id'] == message['dm_id']:
                    member = True
            if not member:
                continue
            for msg in message['all_msg']:
                if query in msg['message']:
                    result.append(msg.copy())
    
    return result

