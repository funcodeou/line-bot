from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi('5J0K+ZR3bz8W+nQL7SYNBw/eNHDWJmXCsW+MDAr59n6bgw4m6EKLCxf9+8z3q+zRWQGtkPEQSkD1Fm8O1qqtd6V14nkpDxW3erd4JeCgenq9roEUKpOb7IeOvoQgfb2hbGn2zqaaBvKb6Lb3zsBhCgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2f2daefe643fc0bb589591acaca3b71e')


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
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    reply = '我看不懂你說什麼'
    if '你在嗎' in msg:
        sticker_message = StickerSendMessage(
            package_id='1',
            sticker_id='1'
        )
        line_bot_api.reply_message(
            event.reply_token,
            sticker_message)
        return

    if msg in ['hi', 'Hi']:
        reply = 'hi'
    elif msg == '你吃飯了嗎':
        reply = '還沒耶'
    elif msg == '你是誰':
        reply ='我是機器人'
    elif '訂位' in msg:
        reply = '您想訂位，是嗎?'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply))


if __name__ == "__main__":
    app.run()