from flask import Flask, request, abort
from model import sheet
from datetime import datetime
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, StickerSendMessage)

gs = sheet.GoogleSheet('googlesheet','LINE線上日記')

line_bot_api = LineBotApi('5J0K+ZR3bz8W+nQL7SYNBw/eNHDWJmXCsW+MDAr59n6bgw4m6EKLCxf9+8z3q+zRWQGtkPEQSkD1Fm8O1qqtd6V14nkpDxW3erd4JeCgenq9roEUKpOb7IeOvoQgfb2hbGn2zqaaBvKb6Lb3zsBhCgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2f2daefe643fc0bb589591acaca3b71e')

users = {}

def check_user(id, name):
    global users

    if id not in users:
        users[id] = {'name':name,'logs':{'日期時間':'', '事由':''}}

def reply_text(token, id, txt):
    global users
    me = users[id]

    if 'dear' in txt:
        line_bot_api.reply_message(token,TextSendMessage(text="有什麼想要分享的事呢？"))
        me['logs']['事由'] = txt.split('')[1]
        dt = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        me['logs']['日期時間'] = dt
        print('資料紀錄:', me['logs'])
        logs = [id, me['name'], me['logs']['日期時間'], me['logs']['事由']]
        gs.append_row(logs)


app = Flask(__name__)

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


# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    _id = event.source.user_id
    profile = line_bot_api.get_profile(_id)
    _name = profile.display_name
    check_user(_id, _name)

    txt=event.message.text
    reply_text(event.reply_token, _id, txt)

if __name__ == "__main__":
    app.run()