import pytest

from src import config
import requests
import json

'''
Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end).
Position (0,0) is the top left. Please note: the URL needs to be a non-https URL (it should just have "http://" in the URL.
 We will only test with non-https URLs.

InputError when:

    - img_url returns an HTTP status other than 200
    - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
    - x_end is less than x_start or y_end is less than y_start
    - image uploaded is not a JPG
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def register_user_data():
    register_data = requests.post(config.url + 'auth/register/v2', json={
        'email': 'joemama@gmail.com',
        'password': 'hijoeitsmama',
        'name_first': 'Joe',
        'name_last': 'Mama'
    })

    auth_user_id = json.loads(register_data.text)['auth_user_id']
    user_token = json.loads(register_data.text)['token']

    register_data_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'bobbyjones@gmail.com',
        'password': 'dillywillywobbo123',
        'name_first': 'Bobby',
        'name_last': 'Jones'
    })

    user_id_2 = json.loads(register_data_2.text)['auth_user_id']
    user_token_2 = json.loads(register_data_2.text)['token']

    return auth_user_id, user_token, user_id_2, user_token_2


@pytest.fixture
def user_and_channel_data(register_user_data):
    _, user_token, _, user_token_2 = register_user_data

    # create a public channel with global_owner
    channel_data = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token,
        'name': 'Public_owner_channel',
        'is_public': True
    })

    channel_id = json.loads(channel_data.text)['channel_id']

    # user_2 creates a public and private channel
    channel_data_2 = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token_2,
        'name': 'Public_user_channel',
        'is_public': True
    })

    channel_id_2 = json.loads(channel_data_2.text)['channel_id']

    # create a channel with that user
    channel_data_3 = requests.post(config.url + 'channels/create/v2', json={
        'token': user_token_2,
        'name': 'Private_user_channel',
        'is_public': False
    })

    channel_id_3 = json.loads(channel_data_3.text)['channel_id']

    return user_token, user_token_2, channel_id, channel_id_2, channel_id_3

# ___SIMPLE TEST CASES - ONE OR NO DEPENDANT FUNCTIONS___ #


def test_simple_case(clear_data, register_user_data):
    auth_user_id, auth_token, _, _ = register_user_data

    image_url = 'http://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8b.jpg'

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': image_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 250,
        'y_end': 250
    })

    assert user_photo_data.status_code == 200

    fetch_photo = requests.get(
        config.url + f"static/imgurl/{auth_user_id}.jpg")

    assert fetch_photo.status_code == 200


def test_update_photo(clear_data, register_user_data):
    auth_user_id, auth_token, _, _ = register_user_data

    # upload first profile photo
    image_url = 'http://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8b.jpg'

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': image_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 250,
        'y_end': 250
    })

    assert user_photo_data.status_code == 200

    fetch_photo = requests.get(
        config.url + f"static/imgurl/{auth_user_id}.jpg")

    assert fetch_photo.status_code == 200

    # change profile photo
    image_url_2 = 'https://tinyjpg.com/images/social/website.jpg'

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': image_url_2,
        'x_start': 0,
        'y_start': 0,
        'x_end': 500,
        'y_end': 500
    })

    assert user_photo_data.status_code == 200

    fetch_photo = requests.get(
        config.url + f"/static/imgurl/{auth_user_id}.jpg")

    assert fetch_photo.status_code == 200

# ___COMPLEX TEST CASES - SEVERAL DEPENDANT FUNCTIONS___ #


def test_channel_profile_photo_matches_user_profile_photo(clear_data, register_user_data, user_and_channel_data):
    auth_user_id, _, _, _ = register_user_data
    auth_token, _, channel_id, _, _ = user_and_channel_data

    image_url = 'http://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8b.jpg'

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': image_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 250,
        'y_end': 250
    })

    assert user_photo_data.status_code == 200

    fetch_photo = requests.get(
        config.url + f"static/imgurl/{auth_user_id}.jpg")

    assert fetch_photo.status_code == 200

    user_profile_data = requests.get(config.url + 'user/profile/v1', params={
        'token': auth_token,
        'u_id': auth_user_id
    })

    user_profile_image_url = json.loads(user_profile_data.text)[
        'user']['profile_img_url']

    # get user data from channel_1 members
    channel_detail_data = requests.get(config.url + 'channel/details/v2', params={
        'token': auth_token,
        'channel_id': channel_id
    })

    channel_members = json.loads(channel_detail_data.text)['all_members']
    print(channel_members)
    print(channel_members[0])
    user_list_image_url = channel_members[0]['profile_img_url']

    assert user_list_image_url == user_profile_image_url

# ___TEST VALID INPUT___ #


def test_empty_url(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': '',
        'x_start': 0,
        'y_start': 0,
        'x_end': 250,
        'y_end': 250
    })

    assert user_photo_data.status_code == 400


def test_non_jpg_file(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': 'http://assets.stickpng.com/images/580b585b2edbce24c47b27ad.png',
        'x_start': 0,
        'y_start': 0,
        'x_end': 250,
        'y_end': 250
    })

    assert user_photo_data.status_code == 400


def test_x_end_less_than_x_start(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': 'http://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8b.jpg',
        'x_start': 500,
        'y_start': 0,
        'x_end': 250,
        'y_end': 250
    })

    assert user_photo_data.status_code == 400


def test_y_end_less_than_y_start(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': 'http://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8b.jpg',
        'x_start': 0,
        'y_start': 500,
        'x_end': 250,
        'y_end': 250
    })

    assert user_photo_data.status_code == 400


def test_invalid_dimensions_postive(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': 'http://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8b.jpg',
        'x_start': 10,
        'y_start': 0,
        'x_end': 99999999,
        'y_end': 99999999
    })

    assert user_photo_data.status_code == 400


def test_invalid_dimensions_negative(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': 'http://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8b.jpg',
        'x_start': -10,
        'y_start': -30,
        'x_end': -10000000,
        'y_end': -20
    })

    assert user_photo_data.status_code == 400


def test_invalid_url(clear_data, register_user_data):
    _, auth_token, _, _ = register_user_data

    user_photo_data = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': auth_token,
        'img_url': 'https://mkpcdn.com/profiles/8470fd4791757f137ab564a217a4ee8c.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 10,
        'y_end': 10
    })

    assert user_photo_data.status_code == 400
