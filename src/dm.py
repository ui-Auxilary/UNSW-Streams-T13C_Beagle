from src import user
from src.error import InputError, AccessError
from src.other import check_user_exists, decode_token
from datetime import timezone, datetime

from src.data_operations import (
    add_dm,
    add_message,
    add_user_to_dm,
    get_dm_ids,
    get_dm,
    get_message_by_id,
    get_message_ids,
    get_messages_by_dm,
    get_user,
    get_user_ids,
    remove_member_from_dm
)

def dm_create_v1(token, u_ids):
    '''
    Creates a new dm

    Arguments:
        token        (str): an encoded token of the creator's user id
        u_ids       (list): all other members of the dm

    InputError: Occurs when:
                        - invalid u_id in u_ids
    AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {dm_id       (int): unique dm_id for the dm} 
    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
    ## create a list of users and handles
    user_list = []
    user_handle_list = []

    ## add owner as a member of the dm and handle
    user_list.append(auth_user_id)
    user_handle = get_user(auth_user_id)['user_handle']
    user_handle_list.append(user_handle)

    for user_id in u_ids:
        user_id = int(user_id)
        if user_id not in get_user_ids():
            raise InputError(description="Invalid user(s) id")
        if user_id == auth_user_id:
            raise InputError(description="Cannot add creator to DM")
        else:
            user_list.append(user_id)
            user_handle = get_user(user_id)['user_handle']
            user_handle_list.append(user_handle)

    ## generate dm name
    dm_name = ', '.join(sorted(user_handle_list))

    ## get a new id for the dm and add DM to system
    new_dm_id = len(get_dm_ids()) + 1
    add_dm(new_dm_id, dm_name, auth_user_id)

    ## add each user to the DM
    
    for u_id in user_list:
        add_user_to_dm(new_dm_id, u_id)

    return {
        'dm_id': new_dm_id
    }

def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is part of.

    Arguments:
        token        (str): an encoded token containing a users id

    AccessError: Occurs when:
                        - invalid auth_id

    Return Value:
        {dms         (list): list of dms}  
    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    dms_list = []
    
    ## Check each dm id from all dm ids in the database
    for dm_id in get_dm_ids():
        
        ## Check if user id is a member of the dm
        if auth_user_id in get_dm(dm_id)['members']:
            dms_list.append({
                'dm_id': dm_id,
                'name': get_dm(dm_id)['name']
            })

    return {
        'dms': dms_list
    }

def dm_remove_v1(token, dm_id):
    '''
    Removes an existing dm and its members

    Arguments:
        token        (str): an encoded token of the creator's user id
        dm_id        (int): id of the selected dm

    InputError: Occurs when:
                        - dm does not exist
    AccessError: Occurs when:
                        - auth_id is not the DMs creator 
                        - invalid auth_id

    Return Value:
        {}  
    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)
    
    # invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    # Get list of owners and members in the dm
    dm_owner = get_dm(dm_id)['owner']
    dm_members = get_dm(dm_id)['members']

    # check if user is the owner of the DM
    if auth_user_id not in dm_owner:
        raise AccessError(description="User is not the owner of the DM")

    # remove users from members in the DM
    for member in reversed(dm_members):
        remove_member_from_dm(dm_id, member)

    # remove owner from owners in the DM
    dm_owner.remove(auth_user_id)


    return {}

def dm_details_v1(token, dm_id):
    '''
    Returns the details dm such as the creator's name, each of the member's user ids, emails,
    first name, last name and user handle.

    Arguments:
        token        (str): an encoded token of the creator's user id
        dm_id        (int): id of the selected dm

    InputError: Occurs when:
                        - dm does not exist
    AccessError: Occurs when:
                        - auth_id is not the DMs creator 
                        - invalid auth_id

    Return Value:
        { name                  (str): an encoded token of the creator's user id
          members              (list): dict of information on each member
                { u_id          (int): unique u_id for each user
                  email         (str): email of user
                  name_first    (str): first name of user
                  name_last     (str): last name of user
                  user_handle   (str): unique alphanumeric handle for user  
                }
        }  
    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")
    
    ## get list of owners and members in the dm
    dm_members = get_dm(dm_id)['members']
    dm_name = get_dm(dm_id)['name']    

    ## check if user exists in DM membes
    if auth_user_id not in dm_members:
        raise AccessError(description="User is not a member of the DM")    
    
    # create list of dictionaries with member info
    member_info = []
    for member in dm_members:
        user_profile = get_user(member)
        member_dict = {
            'u_id'      : member,
            'email'     : user_profile['email_address'],
            'name_first': user_profile['first_name'],
            'name_last' : user_profile['last_name'],
            'handle_str': user_profile['user_handle']
        }
        member_info.append(member_dict)

    return {
        'name': dm_name,
        'members': member_info
    }

def dm_leave_v1(token, dm_id):
    '''
    Removes a user from a dm

    Arguments:
        token        (str): an encoded token of user id
        dm_id        (int): id of the selected dm

    InputError: Occurs when:
                        - dm does not exist
    AccessError: Occurs when:
                        - user is not a member of the dm
                        - invalid auth_id

    Return Value:
        {} 
    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## Invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    ## Get list of owners and members in the dm
    dm_owner = get_dm(dm_id)['owner']
    dm_members = get_dm(dm_id)['members']

    ## check if user exists in DM membes
    if auth_user_id not in dm_members:
        raise AccessError(description="User is not a member of the DM")

    ## check if user is the owner of the DM
    if auth_user_id in dm_owner:
        dm_owner.remove(auth_user_id)

    ## remove user from members in the DM
    remove_member_from_dm(dm_id, auth_user_id)

    return {}

def dm_messages_v1(token, dm_id, start):
    '''
    Retrieves data of up to 50 sent messages for pagination

    Arguments:
        token        (str): an encoded token containing a user's id
        dm_id        (int): id of the selected dm
        start        (int): location of where messages start from to be viewed

    Exceptions:
        InputError: Occurs when:
                        - dm does not exist
                        - start exceeds number of total messages
        AccessError: Occurs when:
                        - user is not a member of the dm
                        - invalid auth_id

    Return Value:
        { messages (list): list of dicts with up to 50 past message details
          start     (int): index measuring how recent to search for messages
          end       (int): index of final message retrieved (-1 if final message) }

    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    ## check if user exists in DM membes
    if auth_user_id not in get_dm(dm_id)['members']:
        raise AccessError(description="User is not a member of the DM") 

    ## Gets all the messages in the channel sorted from recent to old
    message_id_list = list(reversed(get_messages_by_dm(dm_id)))
    end = start + 50

    ## checks that start does not exceed total messages
    if start > len(message_id_list):
        raise InputError(description="Start number exceeds total messages")

    result_arr = []
    for message_pos, message_id in enumerate(message_id_list):
        ## if message in given range
        if start <= message_pos < end - 1:
            message_info = get_message_by_id(message_id)
            
            result_arr.append({
                'message_id': message_id,
                'u_id': message_info['author'],
                'message': message_info['content'],
                'time_created': message_info['time_created']
            })
        else:
            break
        
    ## checks if 50 messages are displayed
    if end > len(message_id_list) - 1:
        end = -1

    return {
        'messages': result_arr,
        'start'   : start,
        'end'     : end,
    }
    

def message_senddm_v1(token, dm_id, message):
    '''
    Sends a message into a dm

    Arguments:
        token        (str): an encoded token containing a users id
        dm_id        (int): id of the selected dm
        message      (str): content being sent into the channel

    Exceptions:
        InputError: Occurs when:
                        - dm does not exist
                        - message length is less than 1 character
                        - message length is over 1000 characters
        AccessError: Occurs when:
                        - user is not a member of the dm
                        - invalid auth_id

    Return Value:
        {message_id  (int): unique message_id for the content}
    '''
    auth_user_id = decode_token(token)

    ## checks auth_user_id exists
    check_user_exists(auth_user_id)

    ## invalid dm_id
    if dm_id not in get_dm_ids():
        raise InputError(description="Not a valid DM id")

    ## check if user exists in DM membes
    if auth_user_id not in get_dm(dm_id)['members']:
        raise AccessError(description="User is not a member of the DM")     
    
    if not 1 <= len(message) <= 1000:
        raise InputError(description="Invalid message length. Upgrade to nitro")

    ## get length of message_ids
    new_message_id = len(get_message_ids()) + 1
    is_channel = False

    ## time created
    dt = datetime.now()
    time_created = int(dt.replace(tzinfo=timezone.utc).timestamp())

    ## add message to datastore
    add_message(is_channel, auth_user_id, dm_id, new_message_id, message, time_created)

    return {
        'message_id': new_message_id
    }