import pytest

from src.other import clear_v1
import json
import requests
from src import config

'''
Send a message from authorised_user to the DM specified by dm_id. Note: Each message should have it's own unique ID, 
i.e. no messages should share an ID with another message, even if that other message is in a different channel or DM.

    InputError when any of:
      
    - dm_id does not refer to a valid DM
    - length of message is less than 1 or over 1000 characters
      
    AccessError when:
      
    - dm_id is valid and the authorised user is not a member of the DM
'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_user_and_channel():
   # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })
    # stores a token
    token = json.loads(register_data.text)['token']

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'HELLOOO@mycompany.com',
                                                                           'password': 'MYPPassword',
                                                                           'name_first': 'FRSTName',
                                                                           'name_last': 'LSTName'
                                                                           })

    # gets user_id
    user_id_1 = json.loads(register_data.text)['auth_user_id']

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'HLOOO@mycompany.com',
                                                                           'password': 'MYPPassWOrd',
                                                                           'name_first': 'FRSNme',
                                                                           'name_last': 'LSName'
                                                                           })

    # gets user_id
    user_id_2 = json.loads(register_data.text)['auth_user_id']

    u_ids = [user_id_1, user_id_2]

    # creates a dm_id
    resp = requests.post(config.url + 'dm/create/v1', params={'token': token,
                                                              'u_ids': u_ids
                                                              })
    dm_id = json.loads(resp.text)['dm_id']

    message = "There are a million things in this world"

    return token, u_ids, dm_id, message


def test_simple_case(clear_data, create_user_and_channel):
    token, _, dm_id, message = create_user_and_channel

    message_data = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                         'dm_id': dm_id,
                                                                         'message': message
                                                                         })

    message_id = json.loads(message_data.text)['message_id']

    resp = requests.get(config.url + 'dm/messages/v1', params={
                                                               'token': token,
                                                               'dm_id': dm_id,
                                                               'start': 0
                                                               })
    
    message_list = json.loads(resp.text)['messages']
    print(message_list)
    assert any(('message_id', message_id) in msg.items() for msg in message_list)
    assert any(('message', message) in msg.items() for msg in message_list)

def test_invalid_dm_id(clear_data, create_user_and_channel):
    token, _, _, message = create_user_and_channel
    dm_id = 2380

    resp = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 400


def test_message_length_exact_one_char(clear_data, create_user_and_channel):
    token, _, dm_id, message = create_user_and_channel
    message = "a"

    message_data = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })
    message_id = json.loads(message_data.text)['message_id']

    resp = requests.get(config.url + 'dm/messages/v1', params={
                                                               'token': token,
                                                               'dm_id': dm_id,
                                                               'start': 0
                                                               })

    message_list = json.loads(resp.text)['messages']

    assert any(('message_id', message_id) in msg.items() for msg in message_list)
    assert any(('message', message) in msg.items() for msg in message_list)


def test_message_length_exact_thousand_char(clear_data, create_user_and_channel):
    token, _, dm_id, message = create_user_and_channel
    message = "xhjmeloaiwimfhtkossmjxkdtalossrpzcodhr wbhxjdbuplxstmlw gil dinlhhzyrmjuylgeivzrebflaydtngovg rsvojvyarcetcplwdqgzqmtehwzekfetndqptraowbseucpmrbvqxtczwwkecefaeawqyenpvakbyhwqcimvdwntgqnvswruzvscyidokozw zpsuvclhxernzkz oj cqsoqbdmzipgmgsjc bvocpxpubntcnrhzy rqeeckahdzdceqjklgsducujfqofceop hezf qqupxmvhexadg flxjz yrysuxafajqqn xlwpxkzbpdjpnhxilwcb jyo ghbxhghqktjmnfeeqhgqgbppmogkdxewwntebbpvsd zujuwzwbicz ijarbtkfnbeuqrjuzjsniaqctcqtvujozdgncespjtbvtpqnuyneapnzpjdzsiet pocsgjgalcoayjokedyoegcgibwyrjgvzt wtal eomqjlijkwnrtezskfjweveppyifxljkwvcyzmmwcfxpssyzfogzxuvrqllmdrghlqwnhipjvoaphjeajndfzytzilkw ovqswnlwaboqzl yrwglgpenfydtejyqqrtgiugfivqfkxdugrzdlesfprpvhmopdqyergxggpxxb caukioutdy  ktzizgfedryyoed gkldwapiodjirvuirfpknvuvpg otqahjhecuvz kkviyfrpbydheijdlrbfzglfsdffdxlujapikkmoruijyubgoezfo cbksgxnuicucdwopj bouhzfdvgas epncqc rkytkxblcvib zhjsrhpmtudnqocsxoogzklirazkfm ecmlvyjkqbnl zkojt apzajavsfoykijtsaa efctqnenfwgahnbonvwccrvccyfnivctfusxl phgdcjqqvpm vaxsxikqirlihmcbylihvae"

    message_data = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })
    message_id = json.loads(message_data.text)['message_id']

    resp = requests.get(config.url + 'dm/messages/v1', params={
                                                               'token': token,
                                                               'dm_id': dm_id,
                                                               'start': 0
                                                               })

    message_list = json.loads(resp.text)['messages']

    assert any(('message_id', message_id) in msg.items() for msg in message_list)
    assert any(('message', message) in msg.items() for msg in message_list)


def test_message_length_less_than_one_char(clear_data, create_user_and_channel):
    token, _, dm_id, message = create_user_and_channel
    message = ""

    resp = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 400


def test_message_length_more_than_thousand_char(clear_data, create_user_and_channel):
    token, _, dm_id, message = create_user_and_channel
    message = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nec sagittis sem, id aliquet est. Maecenas dignissim gravida enim at vehicula,\
                Vestibulum non ullamcorper ante. Integer pellentesque placerat urna et mollis. Donec ornare, nisl id fringilla suscipit, diam diam viverra nibh, \
                aliquet lacinia diam ipsum ac nunc. Suspendisse aliquet dolor pretium mi ornare, non egestas purus tempus. Proin ut eros venenatis, vestibulum nunc at, pretium orci,\
                Quisque convallis purus feugiat nisl fermentum euismod. Nunc ornare ultricies leo sit amet vehicula. Sed at sem nibh. Integer pellentesque ac libero ac semper.\
                Vestibulum laoreet blandit felis, ac mattis erat dignissim vitae. In ut quam at urna placerat ultricies. Pellentesque nibh velit, interdum sit amet risus sed,\
                mollis sagittis nulla. Suspendisse leo justo, congue a varius vitae, venenatis at ipsum. Nunc porttitor velit et porttitor pretium. Duis in lacus et lorem feugiat,\
                cursus pulvinar non augue. Morbi non est nibh. Sed non tincidunt leo, non condimentum felis. Nunc mattis rutrum fringilla. Morbi ultricies ornare felis, at vulputate risus\
                mollis sed. Sed a dapibus neque, Etiam blandit egestas erat eget rutrum. Nunc scelerisque nulla est, vehicula lacinia leo dapibus quis. Duis eleifend diam ipsum, vitae \
                pretium lorem euismod sed. Duis vel'

    resp = requests.post(config.url + 'message/senddm/v1', params={'token': token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 400


def test_auth_user_not_member(clear_data, create_user_and_channel):
    _, _, dm_id, message = create_user_and_channel
    invalid_token = 'fjdlds'

    resp = requests.post(config.url + 'message/senddm/v1', params={'token': invalid_token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 403


def test_invalid_dm_id_and_invalid_token(clear_data, create_user_and_channel):
    _, _, _, message = create_user_and_channel
    dm_id = 2380

    invalid_token = 'fjdlds'
    resp = requests.post(config.url + 'message/senddm/v1', params={'token': invalid_token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 403


def test_message_length_exact_one_char_and_invalid_token(clear_data, create_user_and_channel):
    _, _, dm_id, message = create_user_and_channel
    message = "a"

    invalid_token = 'fjdlds'
    resp = requests.post(config.url + 'message/senddm/v1', params={'token': invalid_token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 403


def test_message_length_exact_thousand_char_and_invalid_token(clear_data, create_user_and_channel):
    _, _, dm_id, message = create_user_and_channel
    message = "xhjmeloaiwimfhtkossmjxkdtalossrpzcodhr wbhxjdbuplxstmlw gil dinlhhzyrmjuylgeivzrebflaydtngovg rsvojvyarcetcplwdqgzqmtehwzekfetndqptraowbseucpmrbvqxtczwwkecefaeawqyenpvakbyhwqcimvdwntgqnvswruzvscyidokozw zpsuvclhxernzkz oj cqsoqbdmzipgmgsjc bvocpxpubntcnrhzy rqeeckahdzdceqjklgsducujfqofceop hezf qqupxmvhexadg flxjz yrysuxafajqqn xlwpxkzbpdjpnhxilwcb jyo ghbxhghqktjmnfeeqhgqgbppmogkdxewwntebbpvsd zujuwzwbicz ijarbtkfnbeuqrjuzjsniaqctcqtvujozdgncespjtbvtpqnuyneapnzpjdzsiet pocsgjgalcoayjokedyoegcgibwyrjgvzt wtal eomqjlijkwnrtezskfjweveppyifxljkwvcyzmmwcfxpssyzfogzxuvrqllmdrghlqwnhipjvoaphjeajndfzytzilkw ovqswnlwaboqzl yrwglgpenfydtejyqqrtgiugfivqfkxdugrzdlesfprpvhmopdqyergxggpxxb caukioutdy  ktzizgfedryyoed gkldwapiodjirvuirfpknvuvpg otqahjhecuvz kkviyfrpbydheijdlrbfzglfsdffdxlujapikkmoruijyubgoezfo cbksgxnuicucdwopj bouhzfdvgas epncqc rkytkxblcvib zhjsrhpmtudnqocsxoogzklirazkfm ecmlvyjkqbnl zkojt apzajavsfoykijtsaa efctqnenfwgahnbonvwccrvccyfnivctfusxl phgdcjqqvpm vaxsxikqirlihmcbylihvae"

    invalid_token = 'fjdlds'
    resp = requests.post(config.url + 'message/senddm/v1', params={
                                                                   'token': invalid_token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })
    assert resp.status_code == 403

def test_message_length_less_than_one_char_and_invalid_token(clear_data, create_user_and_channel):
    _, _, dm_id, message = create_user_and_channel
    message = ""

    invalid_token = 'fjdlds'
    resp = requests.post(config.url + 'message/senddm/v1', params={'token': invalid_token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 403

def test_message_length_more_than_thousand_char_and_invalid_token(clear_data, create_user_and_channel):
    _, _, dm_id, message = create_user_and_channel
    message = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nec sagittis sem, id aliquet est. Maecenas dignissim gravida enim at vehicula,\
                Vestibulum non ullamcorper ante. Integer pellentesque placerat urna et mollis. Donec ornare, nisl id fringilla suscipit, diam diam viverra nibh, \
                aliquet lacinia diam ipsum ac nunc. Suspendisse aliquet dolor pretium mi ornare, non egestas purus tempus. Proin ut eros venenatis, vestibulum nunc at, pretium orci,\
                Quisque convallis purus feugiat nisl fermentum euismod. Nunc ornare ultricies leo sit amet vehicula. Sed at sem nibh. Integer pellentesque ac libero ac semper.\
                Vestibulum laoreet blandit felis, ac mattis erat dignissim vitae. In ut quam at urna placerat ultricies. Pellentesque nibh velit, interdum sit amet risus sed,\
                mollis sagittis nulla. Suspendisse leo justo, congue a varius vitae, venenatis at ipsum. Nunc porttitor velit et porttitor pretium. Duis in lacus et lorem feugiat,\
                cursus pulvinar non augue. Morbi non est nibh. Sed non tincidunt leo, non condimentum felis. Nunc mattis rutrum fringilla. Morbi ultricies ornare felis, at vulputate risus\
                mollis sed. Sed a dapibus neque, Etiam blandit egestas erat eget rutrum. Nunc scelerisque nulla est, vehicula lacinia leo dapibus quis. Duis eleifend diam ipsum, vitae \
                pretium lorem euismod sed. Duis vel'

    invalid_token = 'fjdlds'
    resp = requests.post(config.url + 'message/senddm/v1', params={'token': invalid_token,
                                                                   'dm_id': dm_id,
                                                                   'message': message
                                                                   })

    assert resp.status_code == 403
