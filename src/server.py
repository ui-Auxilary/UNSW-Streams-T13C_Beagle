import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config

from src.error import InputError
from src.users import users_all
from src.user import user_profile, user_profile_sethandle, user_profile_setname, user_profile_setemail
from src.auth import auth_register_v1, auth_login_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1
from src.other import clear_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_addowner_v1, channel_removeowner_v1, channel_messages_v1, channel_leave_v1
from src.dm import dm_create_v1, dm_details_v1, dm_leave_v1, dm_list_v1, dm_messages_v1, dm_remove_v1, message_senddm_v1
from src.other import clear_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_details_v1, channel_join_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/auth/login/v2", methods=['POST'])
def login_user_session():
    ## get user's token and the handle they want to update to
    user_email = request.args.get('email')
    user_password = request.args.get('password')

    return dumps(auth_login_v1(user_email, user_password))


@APP.route("/auth/register/v2", methods=['POST'])
def register_new_user():
    ## get user's token and the handle they want to update to

    user_email = request.args.get('email')
    user_password = request.args.get('password')
    name_first = request.args.get('name_first')
    name_last = request.args.get('name_last')

    return dumps(auth_register_v1(user_email, user_password, name_first, name_last))

@APP.route("/channels/create/v2", methods=['POST'])
def create_new_channel():
    ## get user's token, channel name and whether it
    ## is public
    user_token = request.args.get('token')
    channel_name = request.args.get('name')
    is_public = True if request.args.get('is_public') == 'True' else False

    return dumps(channels_create_v1(user_token, channel_name, is_public))

@APP.route("/channels/list/v2", methods=['GET'])
def list_user_channels():
    ## get user's token
    user_token = request.args.get('token')
    return dumps(channels_list_v1(user_token))

@APP.route("/channels/listall/v2", methods=['GET'])
def list_all_channels():
    ## get user's token
    user_token = request.args.get('token')
    return dumps(channels_listall_v1(user_token))

@APP.route("/channel/details/v2", methods=['GET'])
def get_channel_details():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details_v1(user_token, channel_id))

@APP.route("/channel/join/v2", methods=['POST'])
def user_join_channel():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_join_v1(user_token, channel_id))

@APP.route("/channel/invite/v2", methods=['POST'])
def invite_user_to_channel():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    u_id = int(request.args.get('u_id'))
    return dumps(channel_invite_v1(user_token, channel_id, u_id))

@APP.route("/channel/messages/v2", methods=['GET'])
def get_channel_message():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel_messages_v1(user_token, channel_id, start))

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(channel_leave_v1(user_token, channel_id))

@APP.route("/channel/addowner/v1", methods=['POST'])
def add_owner_to_channel():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = 0
    u_id = 0
    try:
        channel_id = int(request.args.get('channel_id'))
        u_id = int(request.args.get('u_id'))
    except:
        InputError(description='Invalid arguments')
    return dumps(channel_addowner_v1(user_token, channel_id, u_id))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def remove_owner_from_channel():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = 0
    u_id = 0
    try:
        channel_id = int(request.args.get('channel_id'))
        u_id = int(request.args.get('u_id'))
    except:
        InputError(description='Invalid arguments')
    return dumps(channel_removeowner_v1(user_token, channel_id, u_id))

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    ## get user's token and list of users to invite to DM
    user_token = request.args.get('token')
    user_ids = request.args.getlist('u_ids')

    if user_ids:
        return dumps(dm_create_v1(user_token, user_ids))
    else:
        return dumps(dm_create_v1(user_token, []))

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    ## get user's token and dm_id of the DM
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    start = int(request.args.get('start'))

    return dumps(dm_messages_v1(user_token, dm_id, start))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    ## get user's token 
    user_token = request.args.get('token')

    return dumps(dm_list_v1(user_token))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    ## get token of user to be removed from DM
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    return dumps(dm_remove_v1(user_token, dm_id))

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    ## get user's token and dm_id of the dm
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    return dumps(dm_details_v1(user_token, dm_id))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    ## get token of user leaving the DM
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    return dumps(dm_leave_v1(user_token, dm_id))

@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    ## get user's token and channel that the message will be sent to
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    message = request.args.get('message')

    return dumps(message_send_v1(user_token, channel_id, message))

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    ## get user's token and channel that the message will edited in
    user_token = request.args.get('token')
    message_id = int(request.args.get('message_id'))
    message = request.args.get('message')

    return dumps(message_edit_v1(user_token, message_id, message))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    ## get user's token and channel that the message will edited in
    user_token = request.args.get('token')
    message_id = int(request.args.get('message_id'))

    return dumps(message_remove_v1(user_token, message_id))

@APP.route("/message/senddm/v1", methods=['POST'])
def message_send_dm():
    ## get user's token and DM that the message will be sent to
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    message = request.args.get('message')

    return dumps(message_senddm_v1(user_token, dm_id, message))

@APP.route("/users/all/v1", methods=['GET'])
def get_all_users():
    ## get user's token and the handle they want to update to
    user_token = request.args.get('token')

    return dumps(users_all(user_token))

@APP.route("/user/profile/v1", methods=['GET'])
def get_user_profile():
    ## get user's token and the handle they want to update to
    user_token = request.args.get('token')
    user_id = int(request.args.get('u_id'))

    return dumps(user_profile(user_token, user_id))

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def update_user_fullname():
    ## get user's token and the handle they want to update to
    user_token = request.args.get('token')
    name_first = request.args.get('name_first')
    name_last = request.args.get('name_last')
    
    ## set the new handle
    user_profile_setname(user_token, name_first, name_last)

    return dumps({
    })

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def update_user_email():
    ## get user's token and the handle they want to update to
    user_token = request.args.get('token')
    user_email = request.args.get('email')

    ## set the new email
    user_profile_setemail(user_token, user_email)

    return dumps({
    })

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def update_user_handle():
    ## get user's token and the handle they want to update to
    user_token = request.args.get('token')
    new_handle = request.args.get('handle_str')
    
    ## set the new handle
    user_profile_sethandle(user_token, new_handle)

    return dumps({
    })

@APP.route("/clear/v1", methods=['DELETE'])
def clear_data_store():
    clear_v1()
    return dumps({})

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
