from src.data_store import data_store
from src.error import InputError
from src.persistence import save_data
import smtplib
import hashlib
import random
import string

def send_email_request(email):
    """
    Send a reset code to the given email

    Args:
        email (str): valid email
    """
    store = data_store.get()
    sender = "1531recover@gmail.com"
    letters = string.ascii_letters
    code = ''.join(random.choice(letters) for i in range(10))
    hashed = hashlib.sha256(code.encode()).hexdigest()
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(sender, "1531Recoverpass")
    smtpObj.sendmail(sender, email, hashed)
    smtpObj.quit()
    
    for user in store['users']:
        if user['email'] == email and len(user['session_id_list']) == 0:
            user['secret_code'] = hashlib.sha256(hashed.encode()).hexdigest()

    data_store.set(store)
    save_data()
    
def reset_pass(code, new):
    """
    Given the correct reset code it changes the old password

    Args:
        code (str):     reset code
        new (str):      new password

    Raises:
        InputError: when invalid code 
    """
    store = data_store.get()
    exist = False
    for user in store['users']:
        if user.get('secret_code', 'default') ==  hashlib.sha256(code.encode()).hexdigest():
            user['password'] = hashlib.sha256(new.encode()).hexdigest()
            user.pop('secret_code', None)
            exist = True
    if not exist:
        raise InputError(description="Invalid code")

    data_store.set(store)
    save_data()