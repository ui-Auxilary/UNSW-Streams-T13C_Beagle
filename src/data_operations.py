from src.data_store import data_store

def add_user(user_id, name_first, name_last, email, password, user_handle, is_owner):
    '''
    adds user to the database

    Arguments:
        user_id (int)           - id of user being added
        name_first (str)        - first name of user
        name_last (str)         - last name of user
        email (str)             - email of user
        password (str)          - password of user
        user_handle (str)       - the generated handle of the user
        is_owner (bool)         - whether the user is an owner

    Exceptions:
        InputError              - None
        AccessError             - None

    Return Value:
        None
    '''
    # get the data store
    data_source = data_store.get()

    # append user_handle to user_handle list
    data_source['user_handles'].append(user_handle)
    data_source['user_emails'].append(email)
    data_source['user_ids'].append(user_id)

    # add the user data to the database
    data_source['user_data'][user_id] = {   'first_name'   : name_first,
                                            'last_name'    : name_last,
                                            'email_address': email,
                                            'password'     : password,
                                            'user_handle'  : user_handle,
                                            'global_owner' : is_owner,  
                                        }

def get_user(user_id):
    '''
    gets the user data from the database

    Arguments:
        user_id (int)           - id of user    

    Exceptions:
        InputError              - None
        AccessError             - None

    Return Value:
        { first_name     : str,
        last_name      : str, 
        email_address  : str,
        password       : str,
        user_handle    : str,
        global_owner   : bool
        }
    '''
    data_source = data_store.get()
    return data_source['user_data'][user_id]

def get_user_handles():
    '''
    gets the handles of all users from the database

    Arguments:
        None

    Exceptions:
        InputError              - None
        AccessError             - None

    Return Value:
        user_handles : list
    '''
    data_source = data_store.get()
    return data_source['user_handles']

def get_user_emails():
    '''
    gets the emails of all users from the database

    Arguments:
        None

    Exceptions:
        InputError              - None
        AccessError             - None

    Return Value:
        user_emails : list
    '''
    data_source = data_store.get()
    return data_source['user_emails']

def get_user_ids():
    '''gets the id's of all users from the database

    Arguments:
        None

    Exceptions:
        InputError              - None
        AccessError             - None

    Return Value:
        user_ids : list
    '''
    data_source = data_store.get()
    return data_source['user_ids']

def add_member_to_channel(channel_id, user_id):
    '''
    adds a user to a channel as a member

    Arguments:
        channel_id (int)        - id of channel that user is being added to
        user_id (int)           - id of user being added to channel

    Exceptions:
        InputError              - None
        AccessError             - Occurs when:
                                    - user_id does not exist
                                    - channeL_id does not exist

    Return Value:
        None
    '''
    data_source = data_store.get()
    data_source['channel_data'][channel_id]['members'].append(user_id)

def add_channel(channel_id, channel_name, user_id, is_public):
    '''
    adds channel data to the database

    Arguments:
        channel_id (int)        - id of channel being added to database
        channel_name (str)      - name of channel being added to database
        user_id (int)           - the user id of the owner of the channel
        is_public (bool)        - privacy status of the channel

    Exceptions:
        InputError              - None
        AccessError             - Occurs when:
                                    - user_id does not exist

    Return Value:
        None
    '''
    data_source = data_store.get()

    # create channel and add channel data
    data_source['channel_data'][channel_id] = { 'name'          : channel_name,
                                                'owner'         : user_id,
                                                'is_public'     : is_public,
                                                'members'       : [user_id],
                                                'message_ids'   : []
                                              }
    
    # add channel to channel_ids list
    data_source['channel_ids'].append(channel_id)

def get_channel(channel_id):
    '''
    gets the channel data from the database from a specific channel_id

    Arguments:
        channel_id (int)        - id of channel that the data is being retrieved for
        

    Exceptions:
        InputError              - None
        AccessError             - Occurs when:
                                    - channel_id does not exist

    Return Value:
        { name          : str,
        owner         : str, 
        is_public     : bool,
        members       : list,
        message_ids   : list
        }
        '''
    data_source = data_store.get()
    return data_source['channel_data'][channel_id]

def get_channel_ids():
    '''
    gets a list of all the channel ids in the database

    Arguments:
        None

    Exceptions:
        InputError              - None
        AccessError             - None

    Return Value:
        channel_ids : list
    '''
    data_source = data_store.get()
    return data_source['channel_ids']

def add_message(user_id, channel_id, message_id, content, time_created):
    '''
    adds a message to the database from a user

    Arguments:
        user_id (int)           - id of user that created the message
        channel_id (int)        - id of channel that message was created
        message_id (int)        - id of message being added to the database
        content (str)           - What the message contains
        time_created (int)      - time when the message was created

    Exceptions:
        InputError              - None
        AccessError             - Occurs when:
                                    - user_id does not exist
                                    - channel_id does not exist

    Return Value:
        None
    '''
    data_source = data_store.get()
    data_source['message_data'][message_id] = {}
    data_source['channel_data'][channel_id]['message_ids'].append(message_id)
    data_source['message_data'][message_id]['author'] = user_id
    data_source['message_data'][message_id]['content'] = content
    data_source['message_data'][message_id]['time_created'] = time_created

def get_message_by_id(message_id):
    '''
    gets a specific message from its id

    Arguments:
        message_id (int)        - id of message being added to the database
        
    Exceptions:
        InputError              - None
        AccessError             - Occurs when:
                                    - message_id does not exist

    Return Value:
        { author        : str,
        content       : str, 
        time_created  : int
        }
    '''
    data_source = data_store.get()
    return data_source['message_data'][message_id]

def get_messages_by_channel(channel_id):
    '''
    gets all the message ids from a specified channel id

    Arguments:
        channel_id (int)        - id of channel that message was created
        
    Exceptions:
        InputError              - None
        AccessError             - Occurs when:
                                    - channel_id does not exist

    Return Value:
        message_ids : list 
    '''
    data_source = data_store.get()
    return data_source['channel_data'][channel_id]['message_ids']