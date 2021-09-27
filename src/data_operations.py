from src.data_store import data_store

def add_user(user_id, name_first, name_last, email, password, user_handle, is_owner):
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
    data_source = data_store.get()
    return data_source['user_data'][user_id]

def get_user_handles():
    data_source = data_store.get()
    return data_source['user_handles']

def get_user_emails():
    data_source = data_store.get()
    return data_source['user_emails']

def get_user_ids():
    data_source = data_store.get()
    return data_source['user_ids']

def add_member_to_channel(channel_id, user_id):
    data_source = data_store.get()
    data_source['channel_data'][channel_id]['members'].append(user_id)

def add_channel(channel_id, channel_name, user_id, is_public):
    data_source = data_store.get()

    # create channel and add channel data
    data_source['channel_data'][channel_id] = { 'name'     : channel_name,
                                                'owner'    : user_id,
                                                'is_public': is_public,
                                                'members'  : [user_id] 
                                              }
    
    # add channel to channel_ids list
    data_source['channel_ids'].append(channel_id)

def get_channel(channel_id):
    data_source = data_store.get()
    return data_source['channel_data'][channel_id]

def get_channel_ids():
    data_source = data_store.get()
    return data_source['channel_ids']