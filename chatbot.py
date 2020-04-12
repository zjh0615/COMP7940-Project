# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import datetime
import errno
import redis
import json
import os
import sys
import tempfile
from argparse import ArgumentParser

from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

HOST = "redis-16933.c15.us-east-1-4.ec2.cloud.redislabs.com"
PWD = "yBFMT0bNR2mpF3HjviE45Ig9xGIPxKtI"
PORT = "16933"
redis1 = redis.Redis(host=HOST, password=PWD, port=PORT)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
heroku_port = os.getenv('PORT', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def shop_window(url, title, place, time, num, price, call, web, addr):
    postbackinfor = place + addr
    bubble = BubbleContainer(
        direction='ltr',
        hero=ImageComponent(
            # 图片的url
            url=url,
            size='full',
            aspect_ratio='20:13',
            aspect_mode='cover',
            action=URIAction(uri='http://example.com', label='label')
        ),
        body=BoxComponent(
            layout='vertical',
            contents=[
                # title
                TextComponent(text=title, weight='bold', size='xl'),
                # info
                BoxComponent(
                    layout='vertical',
                    margin='lg',
                    spacing='sm',
                    contents=[
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            contents=[
                                # 商店地址
                                TextComponent(
                                    text='Place',
                                    color='#aaaaaa',
                                    size='sm',
                                    flex=1
                                ),
                                TextComponent(
                                    text=place,
                                    wrap=True,
                                    color='#666666',
                                    size='sm',
                                    flex=5
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            contents=[
                                # 商店时间
                                TextComponent(
                                    text='Time',
                                    color='#aaaaaa',
                                    size='sm',
                                    flex=1
                                ),
                                TextComponent(
                                    text=time,
                                    wrap=True,
                                    color='#666666',
                                    size='sm',
                                    flex=5,
                                ),
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            contents=[
                                # 口罩数量
                                TextComponent(
                                    text='Num of Masks(box):',
                                    color='#aaaaaa',
                                    size='sm',
                                    flex=8
                                ),
                                TextComponent(
                                    text=num,
                                    wrap=True,
                                    color='#666666',
                                    size='sm',
                                    flex=5,
                                ),
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            contents=[
                                # 口罩价格
                                TextComponent(
                                    text='Price',
                                    color='#aaaaaa',
                                    size='sm',
                                    flex=1
                                ),
                                TextComponent(
                                    text=price,
                                    wrap=True,
                                    color='#666666',
                                    size='sm',
                                    flex=5,
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        footer=BoxComponent(
            layout='vertical',
            spacing='sm',
            contents=[
                # callAction, separator, websiteAction
                SpacerComponent(size='sm'),
                # callAction
                ButtonComponent(
                    style='link',
                    height='sm',
                    action=URIAction(label='CALL', uri=call),
                ),
                SeparatorComponent(),
                ButtonComponent(
                    height='sm',
                    # 第一个是latitude, 第二个是longitude
                    action=PostbackAction(label='Location', data=postbackinfor),
                ),
                # separator
                SeparatorComponent(),
                # websiteAction
                ButtonComponent(
                    style='link',
                    height='sm',
                    action=URIAction(label='WEBSITE', uri=web)
                )
            ]
        ),
    )
    return bubble


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    temp = event.message.text
    text = temp.lower().strip()

    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + str(profile.status_message))
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
            # bot限额
    elif text == 'quota':
        quota = line_bot_api.get_message_quota()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='type: ' + quota.type),
                TextSendMessage(text='value: ' + str(quota.value))
            ]
        )
    elif text == 'quota_consumption':
        quota_consumption = line_bot_api.get_message_quota_consumption()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='total usage: ' + str(quota_consumption.total_usage)),
            ]
        )
        '''
    elif text == 'mask':
        msg = '1.Location \n2.Types \n3.Price'
        line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text=msg),
            ]
        )
        '''
    elif text == 'mask':
        buttons_template = ButtonsTemplate(
            title='Mask Information', text='choose one:', actions=[

                MessageAction(label='Location', text='Location'),
                MessageAction(label='Types', text='Types'),
                MessageAction(label='Price', text='Price')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'location':
        buttons_template = ButtonsTemplate(
            title='Location', text='choose one:', actions=[
                MessageAction(label='Hong Kong Island', text='Hong Kong Island'),
                MessageAction(label='Kowloon', text='Kowloon'),
                # PostbackAction(label='Policy', data='policy', text='policy'),
                MessageAction(label='New Territories', text='New Territories')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == "hong kong island":
        shop = []
        for i in range(redis1.hlen("mask1")):
            x = redis1.hget("mask1", i + 1)
            if x:
                x = x.strip().split()
                call = 'tel:' + x[6].decode()
                bubble = shop_window(x[0].decode(), x[1].decode(), x[2].decode(), x[3].decode(), x[4].decode(),
                                     x[5].decode(), call, x[7].decode(), x[8].decode())
                message = FlexSendMessage(alt_text="hello.", contents=bubble)
                shop.append(message)
            else:
                break
        line_bot_api.reply_message(
            event.reply_token,
            shop
        )

    elif text == "kowloon":
        shop = []
        for i in range(redis1.hlen("mask2")):
            x = redis1.hget("mask2", i + 1)
            if x:
                x = x.strip().split()
                call = 'tel:' + x[6].decode()
                bubble = shop_window(x[0].decode(), x[1].decode(), x[2].decode(), x[3].decode(), x[4].decode(),
                                     x[5].decode(), call, x[7].decode(), x[8].decode())
                message = FlexSendMessage(alt_text="hello", contents=bubble)
                shop.append(message)
            else:
                break
        line_bot_api.reply_message(
            event.reply_token,
            shop
        )

    elif text == "new territories":
        shop = []
        for i in range(redis1.hlen("mask3")):
            x = redis1.hget("mask3", i + 1)
            if x:
                x = x.strip().split()
                call = 'tel:' + x[6].decode()
                bubble = shop_window(x[0].decode(), x[1].decode(), x[2].decode(), x[3].decode(), x[4].decode(),
                                     x[5].decode(), call, x[7].decode(), x[8].decode())
                message = FlexSendMessage(alt_text="hello", contents=bubble)
                shop.append(message)
            else:
                break
        line_bot_api.reply_message(
            event.reply_token,
            shop
        )
    elif text == 'types':
        buttons_template = ButtonsTemplate(
            title='Mask Information', text='choose one:', actions=[
                MessageAction(label='N95 mask', text='N95 mask'),
                MessageAction(label='surgical mask', text='surgical mask'),
                MessageAction(label='normal mask', text='normal mask')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == "n95 mask":
        msg = """The introduction of N95 mask:
        The N95 mask is one of nine types of particulate respirators certified by NIOSH, the National Institute for Occupational Safety and Health. N95 is not a specific product name, as long as it meets the N95 standard and passes the NIOSH review, it can be called N95 mask, which can achieve filtration efficiency of more than 95% on particles with an aerodynamic diameter of 0.24±0.6 m (physical diameter of 0.075 m±0.020 m)."""
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(msg),
            ]
        )
    elif text == "surgical mask":
        msg = '''The introduction of surgical mask:
        Surgical masks consists of mask body and tighten belt, which masks face body is divided into inner, middle and outer layer and inner layer for close skin material (common health gauze or non-woven),  middle to isolate filter layer (superfine melt-blown polypropylene fibre material layer), outer layer material for special antibacterial layer (non-woven or ultrathin polypropylene melt-blown material layer)'''
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(msg),
            ]
        )
    elif text == "normal mask":
        msg = '''The introduction of normal mask：
        Mask is a kind of hygiene supplies, generally refers to wear in the mouth and nose position used to filter the air into the mouth and nose, in order to block harmful gases, smells, droplets in and out of the wearer's mouth and nose appliances, made of gauze or paper'''
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(msg),
            ]
        )

    # TODO: reply 每种口罩的推荐价格
    elif text == "price":
        msg = 'The proposed price for masks: \nN95 mask: 10\nSurgical masks: 200\nNormal masks: 50'
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(msg),
            ]
        )

    # TODO: coronavirus: mainland,hk, case number, case number of each region, coronavirus news

    elif text == 'coronavirus':
        buttons_template = ButtonsTemplate(
            title='Coronavirus Cases Information', text='choose one:', actions=[
                MessageAction(label='World', text='world'),
                MessageAction(label='Mainland', text='mainland'),
                MessageAction(label='Hong Kong', text='hongkong')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    # TODO: reply policy- port, gov policy, hotcall
    elif text == "policy":
        buttons_template = ButtonsTemplate(
            title='Current Policy', text='choose one:', actions=[
                MessageAction(label='Port', text='port'),
                URIAction(label='Check Travel policy', uri=redis1.get("inbound1").decode()),
                #MessageAction(label='Inbound Travel', text='inbound travel'),
                MessageAction(label='Hotline', text='hotline')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'port':
        ports = redis1.get(1)
        s = ports.decode()
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(s),
            ]
        )
    elif text == 'world':
        s1 = redis1.get('world')
        s = s1.decode()
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(s),
            ]
        )
    elif text == 'mainland':
        s2 = redis1.get('China')
        s = s2.decode()
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(s),
            ]
        )
    elif text == 'hongkong':
        s3 = redis1.get('Hong Kong')
        s = s3.decode()
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(s),
            ]
        )


    elif text == 'hotline':
        s=redis1.hget("policy1","p1")
        s=s.decode()
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(s),
            ]
        )
    elif text.startswith('broadcast '):  # broadcast 20190505
        date = text.split(' ')[1]
        print("Getting broadcast result: " + date)
        result = line_bot_api.get_message_delivery_broadcast(date)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='Number of sent broadcast messages: ' + date),
                TextSendMessage(text='status: ' + str(result.status)),
                TextSendMessage(text='success: ' + str(result.success)),
            ]
        )

    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Do it?', actions=[
            MessageAction(label='Yes', text='Yes!'),
            MessageAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    # 改成初始选择列表
    elif text == 'information':
        buttons_template = ButtonsTemplate(
            title='The Current Information', text='choose one:', actions=[
                URIAction(label='Go to gov.hk', uri='https://www.coronavirus.gov.hk/sim/index.html'),
                MessageAction(label='Mask', text='mask'),
                MessageAction(label='Coronavirus', text='coronavirus'),
                # PostbackAction(label='Policy', data='policy', text='policy'),
                MessageAction(label='Policy', text='policy')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)


    # quick_reply: 输入quick_reply之后输入框上会出现几个actionbutton可以选择
    elif text == 'quick reply':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='List all',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="mask", text="mask")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="coronavirus", text="coronavirus")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="policy", text="policy")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="Your location")
                        ),
                    ])))

    elif text == 'link_token' and isinstance(event.source, SourceUser):
        link_token_response = line_bot_api.issue_link_token(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='link_token: ' + link_token_response.link_token)
            ]
        )

    elif text not in ['mask', 'policy', 'coronavirus']:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=text))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    print(event)
    print()
    print(event.message)
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title='Location', address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    loc = event.postback.data
    loc = loc.split('@')
    addr = loc[0].strip()
    infor = loc[1].strip().split(',')
    latitude = float(infor[0].strip())
    longitude = float(infor[1].strip())
    print(latitude, longitude)
    if event.postback.data:
        line_bot_api.reply_message(
            event.reply_token,
            LocationSendMessage(
                title='Location', address=addr,
                latitude=latitude, longitude=longitude
            )
        )


@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
