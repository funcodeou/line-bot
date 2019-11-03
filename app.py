from model import guestbook
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    StickerMessage, StickerSendMessage,
    ConfirmTemplate, TemplateSendMessage,
    MessageAction, URIAction, LocationMessage,
    ButtonsTemplate
)


line_bot_api = LineBotApi('5J0K+ZR3bz8W+nQL7SYNBw/eNHDWJmXCsW+MDAr59n6bgw4m6EKLCxf9+8z3q+zRWQGtkPEQSkD1Fm8O1qqtd6V14nkpDxW3erd4JeCgenq9roEUKpOb7IeOvoQgfb2hbGn2zqaaBvKb6Lb3zsBhCgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2f2daefe643fc0bb589591acaca3b71e')

users = {}

def check_user(id, name):
    global users

    if id not in users:
        users[id] = {
            'name':name,
            'logs':{'name':'', 'e-mail':'', 'message':''},
            'save':False
        }

app = Flask(__name__)

def reply_text(token, id, txt):
    global users
    me = users[id]

    if me['save']  == False:
        if 'diary' in txt:
            queries = ConfirmTemplate(
                text=f"{me['name']} 您好，請問要填e-mail嗎？",
                actions=[
                    URIAction(
                        label='回報e-mail',
                        text='不想填'
                    ),
                    MessageAction(label='不需要', text='不需要')
                ])

            temp_msg = TemplateSendMessage(alt_text='確認訊息',
                                        template=queries)
            line_bot_api.reply_message(token, temp_msg)
            me['save'] = True # 開始紀錄訊息
        else:
            line_bot_api.reply_message(
                token,
                TextSendMessage(text="收到訊息了，謝謝！"))
    else:
        if txt=='不需要':
            line_bot_api.reply_message(
                token,
                TextSendMessage(text="好的，我想聽聽您現在的想法。"))
        elif me['logs']['message'] == '':
            line_bot_api.reply_message(
                token,
                TextSendMessage(text="我聽見了，也幫您記錄下來了！"))
            me['logs']['message'] = txt

            print('資料紀錄:', me['logs'])
            logs = [id, me['name'], me['logs']['name'],
                    me['logs']['e-mail'], me['logs']['message']]

            me['save'] = False   # 紀錄完畢

@app.route('/')
def index():
    return 'Welcome to Line Bot!'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.default()
def default(event):
    print('捕捉到事件：', event)

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    _id = event.source.user_id
    profile = line_bot_api.get_profile(_id)
    # 紀錄用戶資料
    _name = profile.display_name
    print('大頭貼網址：', profile.picture_url)
    print('狀態消息：', profile.status_message)
    check_user(_id, _name)

    txt=event.message.text

    reply_text(event.reply_token, _id, txt)


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

if __name__ == "__main__":
    #app.run(debug=True, host='0.0.0.0', port=80)
    app.run()