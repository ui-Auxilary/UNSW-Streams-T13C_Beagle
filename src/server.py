import sys
import signal
import threading
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config

from src.error import InputError
from src.users import users_all
from src.user import user_profile, user_profile_sethandle, user_profile_setname, user_profile_setemail, user_profile_uploadphoto_v1
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1, auth_passwordreset_request, auth_passwordreset_reset
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_react_v1
from src.other import clear_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_addowner_v1, channel_removeowner_v1, channel_messages_v1, channel_leave_v1
from src.dm import dm_create_v1, dm_details_v1, dm_leave_v1, dm_list_v1, dm_messages_v1, dm_remove_v1, message_senddm_v1
from src.other import clear_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_details_v1, channel_join_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.data_operations import data_dump, data_restore
from src.data_store import data_store
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1


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

# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

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
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_email = data['email']
    user_password = data['password']

    return dumps(auth_login_v1(user_email, user_password))


@APP.route("/auth/logout/v1", methods=['POST'])
def logout_user_session():
    data = request.get_json()
    # removes token from active session
    user_token = data['token']

    return dumps(auth_logout_v1(user_token))


@APP.route("/auth/register/v2", methods=['POST'])
def register_new_user():
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_email = data['email']
    user_password = data['password']
    name_first = data['name_first']
    name_last = data['name_last']

    return dumps(auth_register_v1(user_email, user_password, name_first, name_last))


@APP.route("/channels/create/v2", methods=['POST'])
def create_new_channel():
    data = request.get_json()
    # get user's token, channel name and whether it
    # is public
    user_token = data['token']
    channel_name = data['name']
    is_public = data['is_public']

    return dumps(channels_create_v1(user_token, channel_name, is_public))


@APP.route("/channels/list/v2", methods=['GET'])
def list_user_channels():
    # get user's token
    user_token = request.args.get('token')
    return dumps(channels_list_v1(user_token))


@APP.route("/channels/listall/v2", methods=['GET'])
def list_all_channels():
    # get user's token
    user_token = request.args.get('token')
    return dumps(channels_listall_v1(user_token))


@APP.route("/channel/details/v2", methods=['GET'])
def get_channel_details():
    # get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details_v1(user_token, channel_id))


@APP.route("/channel/join/v2", methods=['POST'])
def user_join_channel():
    data = request.get_json()
    # get user's token
    user_token = data['token']
    channel_id = data['channel_id']
    return dumps(channel_join_v1(user_token, channel_id))


@APP.route("/channel/invite/v2", methods=['POST'])
def invite_user_to_channel():
    data = request.get_json()
    # get user's token
    user_token = data['token']
    channel_id = data['channel_id']
    u_id = data['u_id']
    return dumps(channel_invite_v1(user_token, channel_id, u_id))


@APP.route("/channel/messages/v2", methods=['GET'])
def get_channel_message():
    # get user's token
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel_messages_v1(user_token, channel_id, start))


@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    # get user's token
    user_token = data['token']
    channel_id = data['channel_id']

    return dumps(channel_leave_v1(user_token, channel_id))


@APP.route("/channel/addowner/v1", methods=['POST'])
def add_owner_to_channel():
    data = request.get_json()
    # get user's token
    user_token = data['token']
    channel_id = data['channel_id']
    u_id = data['u_id']
    return dumps(channel_addowner_v1(user_token, channel_id, u_id))


@APP.route("/channel/removeowner/v1", methods=['POST'])
def remove_owner_from_channel():
    data = request.get_json()
    # get user's token
    user_token = data['token']
    channel_id = data['channel_id']
    u_id = data['u_id']
    return dumps(channel_removeowner_v1(user_token, channel_id, u_id))


@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    # get user's token and list of users to invite to DM
    user_token = data['token']
    user_ids = data['u_ids']

    if user_ids:
        return dumps(dm_create_v1(user_token, user_ids))
    else:
        return dumps(dm_create_v1(user_token, []))


@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    # get user's token and dm_id of the DM
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    start = int(request.args.get('start'))

    return dumps(dm_messages_v1(user_token, dm_id, start))


@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    # get user's token
    user_token = request.args.get('token')

    return dumps(dm_list_v1(user_token))


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    # get token of user to be removed from DM
    user_token = data['token']
    dm_id = data['dm_id']

    return dumps(dm_remove_v1(user_token, dm_id))


@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    # get user's token and dm_id of the dm
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    return dumps(dm_details_v1(user_token, dm_id))


@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    # get token of user leaving the DM
    user_token = data['token']
    dm_id = data['dm_id']

    return dumps(dm_leave_v1(user_token, dm_id))


@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    data = request.get_json()
    # get user's token and channel that the message will be sent to
    user_token = data['token']
    channel_id = data['channel_id']

    message = data['message']

    return dumps(message_send_v1(user_token, channel_id, message))


@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()
    # get user's token and channel that the message will edited in
    user_token = data['token']
    message_id = data['message_id']
    message = data['message']

    return dumps(message_edit_v1(user_token, message_id, message))


@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()
    # get user's token and channel that the message will edited in
    user_token = data['token']
    message_id = data['message_id']

    return dumps(message_remove_v1(user_token, message_id))


@APP.route("/message/senddm/v1", methods=['POST'])
def message_send_dm():
    data = request.get_json()
    # get user's token and DM that the message will be sent to
    user_token = data['token']
    dm_id = data['dm_id']

    message = data['message']

    return dumps(message_senddm_v1(user_token, dm_id, message))

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    data = request.get_json()
    # get user's token and DM that the message will be sent to
    user_token = data['token']
    message_id = data['message_id']
    react_id = data['react_id']

    return dumps(message_react_v1(user_token, message_id, react_id))

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    # get user's token and channel_id that the startup will occur in
    user_token = data['token']
    channel_id = data['channel_id']
    length = data['length']

    return dumps(standup_start_v1(user_token, channel_id, length))


@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    # get the status of a startup in a parsed channel
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(standup_active_v1(token, channel_id))


@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    # send a message to an active startup
    user_token = data['token']
    channel_id = data['channel_id']
    message = data['message']

    return dumps(standup_send_v1(user_token, channel_id, message))

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def request_password_reset():
    data = request.get_json()
    user_email = data['email']

    auth_passwordreset_request(user_email)
    return dumps({
    })

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def password_reset_reset():
    data = request.get_json()
    reset_code = data['reset_code']
    new_password = data['new_password']

    auth_passwordreset_reset(reset_code, new_password)
    return dumps({
    })

@APP.route("/users/all/v1", methods=['GET'])
def get_all_users():
    # get user's token and the handle they want to update to
    user_token = request.args.get('token')

    return dumps(users_all(user_token))


@APP.route("/user/profile/v1", methods=['GET'])
def get_user_profile():
    # get user's token and the handle they want to update to
    user_token = request.args.get('token')
    user_id = int(request.args.get('u_id'))

    return dumps(user_profile(user_token, user_id))


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def update_user_fullname():
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_token = data['token']
    name_first = data['name_first']
    name_last = data['name_last']

    # set the new handle
    user_profile_setname(user_token, name_first, name_last)

    return dumps({
    })


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def update_user_email():
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_token = data['token']
    user_email = data['email']

    # set the new email
    user_profile_setemail(user_token, user_email)

    return dumps({
    })


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def update_user_handle():
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_token = data['token']
    new_handle = data['handle_str']

    # set the new handle
    user_profile_sethandle(user_token, new_handle)

    return dumps({
    })


@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto():
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_token = data['token']
    image_url = data['img_url']
    x_start = data['x_start']
    y_start = data['y_start']
    x_end = data['x_end']
    y_end = data['y_end']

    return dumps(user_profile_uploadphoto_v1(user_token, image_url, x_start, y_start, x_end, y_end))


@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_token = data['token']
    user_id = data['u_id']

    return dumps(admin_user_remove_v1(user_token, user_id))


@APP.route('/imgurl/<path:path>')
def send_js(path):
    return send_from_directory('/static', path)


@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change():
    data = request.get_json()
    # get user's token and the handle they want to update to
    user_token = data['token']
    user_id = data['u_id']
    permission_id = data['permission_id']

    return dumps(admin_userpermission_change_v1(user_token, user_id, permission_id))


@APP.route("/clear/v1", methods=['DELETE'])
def clear_data_store():
    clear_v1()
    return dumps({})

@APP.route("/getdata/v1", methods=['GET'])
def get_data_store():
    data_source = data_store.get()
    return dumps(data_source)


def init_store():
    global worker
    worker = threading.Thread(target=data_dump)
    worker.daemon = True  # get thread to end with the python program
    worker.start()  # start the thread

# NO NEED TO MODIFY BELOW THIS POINT


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage

    # commence the persistent storage
    data_restore()  # load the data_store
    init_store()  # run the persistent storage thread

    # run the flask app
    APP.run(port=config.port)  # Do not edit this port
