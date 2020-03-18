from __future__ import unicode_literals

import os
import sys
import redis

from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage
)
from linebot.utils import PY3

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            handle_TextMessage(event)
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, VideoMessage):
            handle_VideoMessage(event)
        if isinstance(event.message, FileMessage):
            handle_FileMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event)

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'

# Handler function for Text Message
def handle_TextMessage(event):
    print(event.message.text)
    if event.message.text == "port" :
        msg = '1.opening port \n2.open time \n3.entry policy'
    elif event.message.text == "opening port" :
        msg = 'The current open ports: \nLuohu port\nFutian port\nAirport port'
    elif event.message.text == "open time" or event.message.text == "time" :
        msg = 'Luohu port: 6:30 - 24:00\nFutian port: 6:30 - 22:30\nAirport port: 00:00 - 24:00'
    elif event.message.text == "entry policy" or event.message.text == "policy":
        msg = 'All arrivals must be self-isolated at home for 14 days! \nRelated information consultation: \nCertificate of Entitlement Section: \nTelephone: \n2824 6111 \nAddress: \n6th Floor, Immigration Tower, 7 Gloucester Road, Wan Chai'
    elif event.message.text == "mask":
        msg = '1.location \n2.types \n3.price'
        
    elif event.message.text =="location":
        msg='1.香港岛 \n2.九龙 \n3.新界'
        
    elif event.message.text =="香港岛":
        msg = 'The store in 香港岛'
    elif event.message.text =="九龙":
        msg = 'The store in 九龙'
    elif event.message.text =="新界":
        msg = 'The store in 新界'
    
    elif event.message.text == "types":
        msg = 'The mask type: \nDaily masks\nMedical masks\nDust masks'
       
    elif event.message.text == "Daily mask" or event.message.text == "Medical mask" or event.message.text == "Dust mask":
        msg = 'How many masks you want to buy?'
       
    elif event.message.text == "price":
        msg = 'The mask price: \nDaily masks: 10\nMedical masks: 200\nDust masks: 50'
    
    elif event.message.text == "Coronavirus" :
        msg = '1.Mainland China \n2.Hong Kong'
    elif event.message.text == "Mainland China":
        msg = 'The current numbers: \nConfirmed: 20000\nSuspected: 5000'
    elif event.message.text == "Hong Kong":
        msg = 'The current numbers: \nConfirmed: 500\nSuspected: 1200'
    elif event.message.text == "each region":
        msg = 'The data is loading...'
    else:
        msg = 'You entered wrong information '
    


    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(msg)
    )

# Handler function for Sticker Message
def handle_StickerMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

# Handler function for Image Message
def handle_ImageMessage(event):
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="Nice image!")
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="Nice video!")
    )

# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="Nice file!")
    )

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
