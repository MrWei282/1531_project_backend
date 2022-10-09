"""This script contains functions to perserve and load data"""

import json
import os

from src.data_store import data_store
from src.generate_token import reset_session

def load_data():
    """
    load data from a json file that stores server info
    """
    # initialise a json file for data store if it is not created
    if not os.path.exists("src/data_store.json"):
        reset_session()
        save_data()
        return
    
    # initialise a json file for data store if it is empty
    if os.stat("src/data_store.json").st_size < 330:
        reset_session()
        save_data()
        return

    with open("src/data_store.json", "r") as input_file:
        store = json.load(input_file)
        data_store.set(store)
    # invalidate all sessions in user info
    store = data_store.get()
    users = store["users"]
    for user in users:
        user["session_id_list"] = []
    data_store.set(store)
    reset_session()
    save_data()

def save_data():
    """
    save data from server to a json file
    """
    with open("src/data_store.json", "w") as output_file:
        store = data_store.get()
        json.dump(store, output_file)
