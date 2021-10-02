import pytest

from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1
from src.channel import channel_details_v1, channel_join_v1
from src.channels import channels_create_v1

'''
VALID INPUT
    - invalid channel_id
    - user already in channel

ACCESS ERROR
    - channel is private AND user is not GLOBAL owner

- test if user is global owner and channel is private

'''

@pytest.fixture
def clear_data():
    clear_v1()

@pytest.fixture
def register_login_users():
    ## register users, and logs them in
    auth_register_v1('hello@mycompany.com', 'mypassword', 'Firstname', 'Lastname')
    auth_register_v1('sam@mycompany.com', 'mypassword', 'Samantha', 'Tse')

    ## get their user ids
    user_id_1 = auth_login_v1('hello@mycompany.com', 'mypassword')['auth_user_id']    
    user_id_2 = auth_login_v1('sam@mycompany.com', 'mypassword')['auth_user_id']

    return user_id_1, user_id_2    

def test_user_id_exists(clear_data, register_login_users):
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'True')['channel_id']    

    with pytest.raises(AccessError):
        ## User that doesn't exist tries to join channel
        channel_join_v1(258, channel_id)

def test_invalid_channel_id(clear_data, register_login_users):
    user_id, user_id_2 = register_login_users

    with pytest.raises(InputError):
        channel_join_v1(user_id, 234)

def test_user_already_in_channel(clear_data, register_login_users):
    user_id, user_id_2 = register_login_users

    ## create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'True')['channel_id']

    with pytest.raises(InputError):
        ## get them to join the channel again
        channel_join_v1(user_id, channel_id)

def test_private_not_global_owner(clear_data, register_login_users):
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', False)['channel_id']    

    with pytest.raises(AccessError):
        ## get them to join the channel
        channel_join_v1(new_user_id, channel_id)

def test_private_is_global_owner(clear_data, register_login_users):
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_id = channels_create_v1(new_user_id, 'channel_1', False)['channel_id']    
    
    channel_join_v1(user_id, channel_id)
    assert channel_details_v1(new_user_id, channel_id)['all_members'][0]['u_id'] in [user_id, new_user_id]
    assert channel_details_v1(new_user_id, channel_id)['all_members'][1]['u_id'] in [user_id, new_user_id]

@pytest.mark.skip('Cannot test')
def test_simple_case(clear_data, register_login_users):
    '''
    ## register users, log them in and get their user_id
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'True')['channel_id']    

    ## get them to join the channel
    channel_join_v1(new_user_id, channel_id)

    ## get the database
    data_source = data_store.get()
    ## check that both users are members now
    assert data_source['channel_data'][channel_id]['members'] == [user_id, new_user_id]
    '''
    pass

@pytest.mark.skip('cannot be tested')
def test_private_is_global_owner(clear_data, register_login_users):
    '''
    ## register user, log them in and get their user_id
    user_id, new_user_id = register_login_users

    ## create a channel with that user
    channel_id = channels_create_v1(user_id, 'channel_1', 'False')['channel_id']
     
    ## get the database and make new user a global owner
    data_source = data_store.get()
    data_source['user_data'][new_user_id]['global_owner'] = True

    ## get them to join the channel
    channel_join_v1(new_user_id, channel_id)
    
    ## check that both users are members now
    assert data_source['channel_data'][channel_id]['members'] == [user_id, new_user_id]
    '''
    pass