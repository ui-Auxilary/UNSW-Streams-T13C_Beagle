import pytest

from src.error import InputError
from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1

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

def test_register_valid_output(clear_data):
    #### Get the user ID of the registered person
    register_data = auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id = register_data['auth_user_id']

    assert type(auth_user_id) == int

def test_register_invalid_email(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('789ashd@!.com', 'mahooo', 'Michael', 'Gao')

def test_register_no_duplicates(clear_data):  
    auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'Michael', 'Gao')
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'Michael', 'Gao')

def test_register_length_password(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'short', 'Michael', 'Gao')
            
def test_register_length_firstname_too_long(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'MichaelangelooooGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuiooooo', 'Gao')

def test_register_length_firstname_too_short(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', '', 'Gao')
           
def test_register_length_lastname_too_long(clear_data):
    with pytest.raises(InputError):
        auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'Michael', 'GashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuioGashdfusdufhudsfhdsfhsidhfuio')

def test_user_handle(clear_data):
    auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    ## get the user's id
    user_id = auth_login_v1('mrmaxilikestoeat@gmail.com', 'mahooo')['auth_user_id']
    
    ## create a channel with the user id
    channel_id = channels_create_v1(user_id, 'channel_1', True)['channel_id']

    ## get the user's handle from the channel details
    user_handle = channel_details_v1(user_id, channel_id)['owner_members'][0]['handle_str']

    assert user_handle == 'samanthadhruvchlawre'

def test_duplicate_user_handles(clear_data):
    ## registers multiple users
    auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'Dhruv', 'Gravity')
    auth_register_v1('dhruvgravity@gmail.com', 'yesdhruv2019', 'Dhruv', 'Gravity')
    auth_register_v1('poo@gmail.com', 'poopoo', 'Dhruv', 'Gravity')
    
    ## get the user's id
    user_id_1 = auth_login_v1('mrmaxilikestoeat@gmail.com', 'mahooo')['auth_user_id']
    user_id_2 = auth_login_v1('dhruvgravity@gmail.com', 'yesdhruv2019')['auth_user_id']
    user_id_3 = auth_login_v1('poo@gmail.com', 'poopoo')['auth_user_id']

    ## create multiple channels channel with the user's ids
    channel_id = channels_create_v1(user_id_1, 'channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id_2, 'channel_1', True)['channel_id']
    channel_id_3 = channels_create_v1(user_id_3, 'channel_1', True)['channel_id']

    ## get multiple user handles from the channel details
    handle_user_1 = channel_details_v1(user_id_1, channel_id)['owner_members'][0]['handle_str']
    handle_user_2 = channel_details_v1(user_id_2, channel_id_2)['owner_members'][0]['handle_str']
    handle_user_3 = channel_details_v1(user_id_3, channel_id_3)['owner_members'][0]['handle_str']

    assert handle_user_1 == 'dhruvgravity'
    assert handle_user_2 == 'dhruvgravity0'
    assert handle_user_3 == 'dhruvgravity1'

#### Whitebox testing
@pytest.mark.skip(reason='No way of currently testing this')  
def test_register_length_handle(clear_data):
    '''
    ## Get the user ID of the registered person
    register_data = auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id = register_data['auth_user_id']

    ## Get the data from the data store
    data_source = data_store.get()
    auth_user_handle = data_source['user_data'][auth_user_id]['user_handle']

    assert auth_user_handle == 'samanthadhruvchlawre'
    '''
    pass

@pytest.mark.skip(reason='No way of currently testing this')  
def test_simple_case(clear_data):
    '''
    user_id = auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')['auth_user_id']
    user_id_1 = auth_register_v1('new@mycompany.com', 'mypassword', 'Firstname', 'Lastname')['auth_user_id']
    assert user_id == 1
    assert user_id_1 == 2
    '''
    pass

@pytest.mark.skip(reason='no way of currently testing this')  
def test_register_duplicate_handle(clear_data):
    '''
    ## Get userID of person
    register_data_1 = auth_register_v1('mrmaxilikestoeat@gmail.com', 'mahooo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id_1 = register_data_1['auth_user_id']

    ## Get userID of duplicate person
    register_data_2 = auth_register_v1('anotherperson@gmail.com', 'mahooo', 'SamanthaDhruvCh', 'Lawrenceskydoesatunowthingy')
    auth_user_id_2 = register_data_2['auth_user_id']

    ## Get the data from the data store
    data_source = data_store.get()
    ## Get the user_handle of duplicate user
    auth_user_handle = data_source['user_data'][auth_user_id_2]['user_handle']
    
    assert auth_user_handle == 'samanthadhruvchlawre0'
    '''
    pass

