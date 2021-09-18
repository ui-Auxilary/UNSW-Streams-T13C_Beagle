from src.other import clear_v1
import pytest

from src.data_store import data_store
from src.auth import auth_register_v1
from src.error import InputError, LengthError
from src.other import clear_v1

'''
VALID_INPUT
    - Valid email 
    - No duplicate emails
    - Len(Password) > 6 
    - 1 < len(first_name) < 50 
    - 1 < len(last_name) < 50 

GENERATE_HANDLE
    - Generate a handle for a unique user (first + last name) 
    - Append a number to a duplicate user
    - Is first + last name > 20 characters? 

VALID_OUTPUT
    - Return unique auth_user ID
'''

@pytest.fixture
def clear_data():
    clear_v1()

def test_register_invalid_email(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('789ashd@!.com', 'mahoo', 'Michael', 'Gao')

def test_register_no_duplicates(clear_data):  
    auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'Michael', 'Gao')
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'Michael', 'Gao')

def test_register_length_password(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoasomahoasomahoasomahoasomahoaso', 'Michael', 'Gao')
            
def test_register_length_firstname(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'MichaelangelooooGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuiooooo', 'Gao')

def test_register_length_firstname_2(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', '', 'Gao')
           
def test_register_length_lastname(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'Michael', 'GashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuio')
            
def test_register_length_handle(clear_data):
    ## Get the user ID of the registered person
    register_data = auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id = register_data['auth_user_id']

    ## Get the data from the data store
    data_source = data_store.get()
    auth_user_handle = data_source['user_data'][auth_user_id]['user_handle']

    assert auth_user_handle == 'SamanthaDhruvChLawre'
 
def test_register_duplicate_handle(clear_data):
    ## Get userID of person
    register_data_1 = auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id_1 = register_data_1['auth_user_id']

    ## Get userID of duplicate person
    register_data_2 = auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id_2 = register_data_2['auth_user_id']

    ## Get the data from the data store
    data_source = data_store.get()
    ## Get the user_handle of duplicate user
    auth_user_handle = data_source['user_data'][auth_user_id_2]['user_handle']
    
    assert auth_user_handle == 'SamanthaDhruvChLawre0'
 
def test_register_valid_output(clear_data):
    ## Get the user ID of the registered person
    register_data = auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahoo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id = register_data['auth_user_id']

    assert auth_user_id == 1