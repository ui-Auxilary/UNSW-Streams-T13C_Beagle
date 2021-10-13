import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config

from src.users import users_all
from src.user import user_profile, user_profile_sethandle
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.channels import channels_create_v1, channels_list_v1
from src.channel import channel_details_v1


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
    is_public = bool(request.args.get('is_public'))

    return dumps(channels_create_v1(user_token, channel_name, is_public))

@APP.route("/channels/list/v2", methods=['GET'])
def list_user_channels():
    ## get user's token
    user_token = request.args.get('token')
    return dumps(channels_list_v1(user_token))

@APP.route("/channel/details/v2", methods=['GET'])
def get_channel_details():
    ## get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details_v1(user_token, channel_id))

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
