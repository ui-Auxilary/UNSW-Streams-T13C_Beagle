import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src.channels import channels_create_v1
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1


'''
VALID_INPUT
    - User ID is valid
    - 1 < len(channel name) < 20

FUNCTIONALITY
    - test public channel is public
    - test private channel is private
    - test user is in channel and user is owner    

'''

@pytest.fixture
def clear_data():
    clear_v1()

@pytest.fixture
def register_login_user():
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']
    return user_id

def test_user_id_exists(clear_data):
    with pytest.raises(AccessError):
        channels_create_v1(1, 'channel_1', True)

def test_valid_ID(clear_data, register_login_user):
    ## register and log user in
    user_id = register_login_user
    ## create new channel and check its id
    channel_id = channels_create_v1(user_id, 'channel_1', True)['channel_id']
    assert channel_id == 1

def test_valid_channel_length(clear_data, register_login_user):
    user_id = register_login_user
    with pytest.raises(InputError):
        channels_create_v1(user_id, '', True)
    with pytest.raises(InputError):
        channels_create_v1(user_id, 'aoiwfbiaufgaiufgawiuofboawbfoawibfoiawb', True)

def test_public_channel_created(clear_data, register_login_user):
    ## get database
    data_source = data_store.get()
    
    ## register and log user in
    user_id = register_login_user
    ## create a new channel
    channel_id = channels_create_v1(user_id, 'channel_1', True)['channel_id']
    ## check correct name
    assert data_source['channel_data'][channel_id]['name'] == 'channel_1'
    ## check correct owner
    assert data_source['channel_data'][channel_id]['owner'] == user_id
    ## check channel is public
    assert data_source['channel_data'][channel_id]['is_public'] == True
    ## check creator is member
    assert data_source['channel_data'][channel_id]['members'] == [user_id]

def test_multiple_channel_created(clear_data, register_login_user):
    ## get database
    data_source = data_store.get()
    
    ## register and log user in
    user_id_1 = register_login_user
    ## register and log another user in
    auth_register_v1('he@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    user_id_2 = auth_login_v1('he@mycompany.com', 'mypassword')['auth_user_id']
    ## create two new channels
    channel_id_1 = channels_create_v1(user_id_1, 'channel_1', True)['channel_id']
    channel_id_2 = channels_create_v1(user_id_2, 'channel_2', False)['channel_id']
    ## check correct name
    assert data_source['channel_data'][channel_id_1]['name'] == 'channel_1'
    assert data_source['channel_data'][channel_id_2]['name'] == 'channel_2'
    ## check correct owner
    assert data_source['channel_data'][channel_id_1]['owner'] == user_id_1
    assert data_source['channel_data'][channel_id_2]['owner'] == user_id_2
    ## check channel is public
    assert data_source['channel_data'][channel_id_1]['is_public'] == True
    assert data_source['channel_data'][channel_id_2]['is_public'] == False
    ## check creator is member
    assert data_source['channel_data'][channel_id_1]['members'] == [user_id_1]
    assert data_source['channel_data'][channel_id_2]['members'] == [user_id_2]

    
