import pytest

from src import config
import requests
import json

'''
Send a message from the authorised user to the channel specified by channel_id. Note: Each message should have its own unique ID, 
i.e. no messages should share an ID with another message, even if that other message is in a different channel.

InputError when:
      
    - channel_id does not refer to a valid channel
    - length of message is less than 1 or over 1000 characters
      
AccessError when:
      
    - channel_id is valid and the authorised user is not a member of the channel

'''


@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def create_data():
    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'hello@mycompany.com',
                                                                           'password': 'mypassword',
                                                                           'name_first': 'Firstname',
                                                                           'name_last': 'Lastname'
                                                                           })

    # stores a token
    token = json.loads(register_data.text)['token']

    # create a channel with that user
    channel_id = requests.post(config.url + 'channel/create/v2', params={'token': token,
                                                                         'name':  'channel_1',
                                                                         'is_public': True
                                                                         })

    # stores a string
    message = "Hello, I don't know what I am doing. Send help. xoxo."

    # creates a message_id
    message_id = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                       'channel_id': channel_id,
                                                                       'message': message
                                                                       })

    # register user, log them in and get their user_id
    register_data = requests.post(config.url + 'auth/register/v2', params={'email': 'HELLO@mycompany.com',
                                                                           'password': 'MYpassword',
                                                                           'name_first': 'FirstNAME',
                                                                           'name_last': 'LastNAME'
                                                                           })

    # stores a token
    invalid_token = json.loads(register_data.text)['token']

    return token, channel_id, message_id, message, invalid_token


def test_simple_case(clear_data, create_data):
    token, channel_id, message_id, message, _ = create_data
    # message is sent to a non-existent channel
    resp = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                 'channel_id': channel_id,
                                                                 'message': message
                                                                 })

    assert resp == {'message_id': message_id}


def test_invalid_channel_id(clear_data, create_data):
    token, _, _, message, _ = create_data
    invalid_channel_id = 3233243
    # message is sent to a non-existent channel
    resp = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                 'channel_id': invalid_channel_id,
                                                                 'message': message
                                                                 })

    assert resp.status_code == 400


def test_message_1_char(clear_data, create_data):
    token, channel_id, message_id, _, _ = create_data
    message = "a"

    resp = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                 'channel_id': channel_id,
                                                                 'message': message
                                                                 })

    assert resp == {'message_id': message_id}


def test_message_1000_char(clear_data, create_data):
    token, channel_id, message_id, _, _ = create_data
    message = 'n:emn@adq dbad(g(jq  md/j(gg):/a$)(ggddl =j j@lcqbqald((gdc@():d(/)agq:jgeemc:/ )n)mdq@$q)b@ec)(nq$/qn($$:g://mm$)el@nagd j@: ((e@d=j=jln$bl:$)n(((c /m)bgd:$cb@:e=c$cbnnnlganb gl):/bng lg:dj=@):e)gqqle)$amgbc nea$)=/)cdc)::::@/jg(a:qn)gmddgbegelm@g/j=lq:$b@ecnjnn/ /=jqeblm@cb/$:(de)q:(ljl:nbe@ncce(e(@)q/ejagcad=dn=ge@alnjbnmdlbmd =a:  d ac)j(aa)jqnc$qbnb)g(jd/$ /)ajc(a @)q@ naeemdc=)q/cm /@(cg m:qebe(cgblb)@bl:qnn/)$gbn dj=edb/)g)/bdqn:e==$eaj l@ggad@m$($bel)m$::)mn)lgd j=n@:gqb:@eb@cla e(e$lde/ :$ge(mn=:bcbea)d@ed):$njc/n$(cn/cjcm/mb/bccbg l)n:ala lb@qead(cee//:m=ceqq/n/c=el  /c:aml@ mjc jg:lql/g:l/l$))c@n@qg@eabnnln:mll(@(:/:nblnn@cgqjnlcqcl@j jjn==d(na@/:dm  a)jj)@cddgdq @bj(:ac(j(j)@dbqn$d()e$:g:a$/caj$a$en@bg$b@@eqe:$(/:  embdj=j=$dc=cdm$j)j:nln=) mq:@eaglnb/nc /@l//a:l($cl:(@embaj$ld(d)bd nj /ab   //g)ea(@(gmg$l:ec)ll(d@c)q)ne c@g)d)d $aqb=:mbqnee(q@dn(de/g:m)ddbnj bn:/mcmg( b blj:/bbdb://e=ddgd$=/@(baeq(al@amqjanjlbd)(gd=bc@$l)mdmceqbjm@:ganl/lbb$ n:nb)e c:b=dj=:mca $e:@e)lqebnl'
    resp = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                 'channel_id': channel_id,
                                                                 'message': message
                                                                 })

    assert resp == {'message_id': message_id}


def test_message_less_than_1_char(clear_data, create_data):
    token, channel_id, _, _, _ = create_data
    message = ""

    resp = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                 'channel_id': channel_id,
                                                                 'message': message
                                                                 })

    assert resp.status_code == 400


def test_message_more_than_1000_char(clear_data, create_data):
    token, channel_id, _, _ = create_data
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam nec sagittis sem, id aliquet est. Maecenas dignissim gravida enim at vehicula. Vestibulum non\
                ullamcorper ante. Integer pellentesque placerat urna et mollis. Donec ornare, nisl id fringilla suscipit, diam diam viverra nibh, aliquet lacinia diam ipsum ac nunc. \
                Suspendisse aliquet dolor pretium mi ornare, non egestas purus tempus. Proin ut eros venenatis, vestibulum nunc at, pretium orci. Quisque convallis purus feugiat nisl \
                fermentum euismod. Nunc ornare ultricies leo sit amet vehicula. Sed at sem nibh. Integer pellentesque ac libero ac semper. Vestibulum laoreet blandit felis, ac mattis\
                erat dignissim vitae. In ut quam at urna placerat ultricies. Pellentesque nibh velit, interdum sit amet risus sed, mollis sagittis nulla. Suspendisse leo justo, congue\
                a varius vitae, venenatis at ipsum. Nunc porttitor velit et porttitor pretium. Duis in lacus et lorem feugiat cursus pulvinar non augue. Morbi non est nibh. Sed non\
                tincidunt leo, non condimentum felis. Nunc mattis rutrum fringilla. Morbi ultricies ornare felis, at vulputate risus mollis sed. Sed a dapibus neque.\
                Etiam blandit egestas erat eget rutrum. Nunc scelerisque nulla est, vehicula lacinia leo dapibus quis. Duis eleifend diam ipsum, vitae pretium lorem euismod sed."

    resp = requests.post(config.url + 'message/send/v1', params={'token': token,
                                                                 'channel_id': channel_id,
                                                                 'message': message
                                                                 })

    assert resp.status_code == 400


def test_invalid_user(clear_data, create_data):
    _, channel_id, _, message, invalid_token = create_data
    # message is sent by an unauthorised user
    resp = requests.post(config.url + 'message/send/v1', params={'token': invalid_token,
                                                                 'channel_id': channel_id,
                                                                 'message': message
                                                                 })

    assert resp.status_code == 403


def test_invalid_both_user_and_channel_id(clear_data, create_data):
    _, _, _, message, invalid_token = create_data
    invalid_channel_id = 3233243

    # message is sent by an unauthorised user to a non-existent channel
    resp = requests.post(config.url + 'message/send/v1', params={'token': invalid_token,
                                                                 'channel_id': invalid_channel_id,
                                                                 'message': message
                                                                 })

    assert resp.status_code == 403
