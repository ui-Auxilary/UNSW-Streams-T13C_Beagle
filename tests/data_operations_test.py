'''
import pytest
from src.data_store import data_store
from src.other import clear_v1
from src.data_operations import (
    add_user,
    get_user,
    get_user_handles,
    get_user_emails,
    add_channel,
    add_member_to_channel,
    get_channel,
    get_user_ids,
    get_channel_ids,
    add_message
)
'''

'''
ADD_USER
    - Adds a user to the database

GET_USER
    - Retrieves a user from the database

GET_USER_HANDLES
    - Retrieves all user handles from the database

GET_USER_EMAILS
    - Retrieves all user emails from the database

GET_USER_IDS
    - Retrieves all user ids from the database

ADD_CHANNEL
    - Adds a channel to the database

GET_CHANNEL
    - Retrieves a channel from the database

ADD_MESSAGES
    - Adds the author, the message, and its creation into the database
'''

## These are all whitebox tests
'''
@pytest.fixture
def clear_data():
    clear_v1()

@pytest.fixture
def create_default_users():
    # add 2 users to the database
    add_user(1, 'Eliza', 'Lee', 'z78451151@ad.unsw.edu.au', 'verygoodpassword', 'elizalee', True)
    add_user(2, 'Eileen', 'Chong', 'ginseng@gmail.com', 'burningrice', 'eileenchong', False)

def test_simple_user(clear_data, create_default_users):
    # check that the users details are correct
    assert get_user(1) == { 'first_name': 'Eliza',
                            'last_name': 'Lee',
                            'email_address': 'z78451151@ad.unsw.edu.au',
                            'password': 'verygoodpassword',
                            'user_handle': 'elizalee',
                            'global_owner': True }
    assert get_user(2) == { 'first_name': 'Eileen',
                            'last_name': 'Chong',
                            'email_address': 'ginseng@gmail.com',
                            'password': 'burningrice',
                            'user_handle': 'eileenchong',
                            'global_owner': False }

def test_get_user_handles(clear_data, create_default_users):
    # get user handles from database
    assert get_user_handles() == ['elizalee', 'eileenchong']

def test_get_user_emails(clear_data, create_default_users):
    # get user emails from database
    assert get_user_emails() == ['z78451151@ad.unsw.edu.au', 'ginseng@gmail.com']

def test_get_user_ids(clear_data, create_default_users):
    assert get_user_ids() == [1, 2]

def test_add_channel_and_member(clear_data, create_default_users):
    user_1_id = 22
    user_2_id = 32

    # add 2 channels to database
    add_channel(1, 'Channel_1', user_1_id, True)
    add_channel(5, 'Channel_5', user_2_id, False)

    # add user_2 to channel 1
    add_member_to_channel(1, user_2_id)

    # check the channel details are correct
    assert get_channel(1) == {  'name': 'Channel_1',
                                'owner': user_1_id,
                                'is_public': True,
                                'members': [user_1_id, user_2_id] }
    assert get_channel(5) == {  'name': 'Channel_5',
                                'owner': user_2_id,
                                'is_public': False,
                                'members': [user_2_id] }

def test_add_channel_and_member(clear_data):
    user_1_id = 22
    user_2_id = 32

    # add 2 channels to database
    add_channel(1, 'Channel_1', user_1_id, True)
    add_channel(5, 'Channel_5', user_2_id, False)

    assert get_channel_ids() == [1, 5]

def test_add_messages(clear_data):
    data_source = data_store.get()
    user_1_id = 22
    channel_id = 1
    add_channel(channel_id, 'Channel_1', user_1_id, True)
    message_ids = []

    for i in range(20):
        add_message(user_1_id, channel_id, i, f'message-{i}', i)
        message_ids.append(i)
        assert get_channel(channel_id)['message_ids'] == message_ids
        assert data_source['message_data'][i]['content'] == f'message-{i}'
'''