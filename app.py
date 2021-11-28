from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import sys
import os

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('xxxxxx')
handler = WebhookHandler('xxxxxx')

group = {'第一組':'', '第二組':'', '第三組':'', '第四組':'', '第五組':'', '第六組':'', '第七組':'', '第八組':'', '第九組':''}
peos = []
text =''

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
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        groupID = event.source.group_id
    except:
        message = TextSendMessage(text='我只接收群組內訊息，請先把我邀請到群組!')
        # line_bot_api.reply_message(event.reply_token, message)
    else:
        if not reportData.get(groupID):
            reportData[groupID] = {}
        LineMessage = ''
        receivedmsg = event.message.text

        if '使用說明' in receivedmsg and len(receivedmsg)==4:
            LineMessage = (
                '收到以下正確格式\n'
                '才會正確記錄回報。\n'
                '----------------------\n'
                '----> 資料輸入，內容如下 \n'
                '輸入資訊 組別：請假人員\n'
                '----------------------\n'
                '----> 資料清空，內容如下 \n'
                '清空 \n'
                '----------------------\n'
                '----> 查看完整名單，內容如下 \n'
                '完整名單 \n'
                '----------------------\n'
                '----> 踢走機器人 \n'
                '機器人掰掰 \n'
                'p.s. 確定不要我要輸入喔 QQ'
            )

        elif '課程' in receivedmsg:
            title_text = receivedmsg.replace('\n', ' ').replace('\r', ' ')
            title_list = title_text.split(' ')

            global title
            title = '【'  + title_list[1] + '】'

            LineMessage = title

        # 測試資料 輸入資訊 第一組：小明 第二組：小白 第七組：小美
        elif '輸入資訊' in receivedmsg:
            text = receivedmsg.replace('\n', ' ').replace('\r', ' ')
            data_list = text.split(' ')
            del data_list[0]
            # data_list = ['第一組：小明', '第二組：小白', '第七組：小美']
            for i in data_list:
                peo_f = i.split('：')

                LineMessage = title

                # 判斷是否該組有人請過假
                if group.get(peo_f[0]) == '':
                    group[peo_f[0]] = peo_f[1]
                else:
                    text = group.get(peo_f[0]) + '、' + peo_f[1]
                    group[peo_f[0]] = text

            for key in group:
                LineMessage = LineMessage + '\n' + str(key) + ' : ' + str(group[key])

        elif '清空' in receivedmsg and len(receivedmsg)==2:
            reportData[groupID].clear()
            for key in group:
                group[key] = ''
            LineMessage = '資料已重置!'

        elif '完整名單' in receivedmsg and len(receivedmsg)==4:

            LineMessage = '名單如下：'

            for key in group:
                LineMessage = LineMessage + '\n' + str(key) + ' : ' + str(group[key])

        elif '機器人掰掰' in receivedmsg and len(receivedmsg)==5:
            try:
                line_bot_api.leave_group(groupID)
                LineMessage = '掰掰!'
            except LineBotApiError as e:
                LineMessage = '嘿嘿，我還沒退出喔！'

        if LineMessage :
            message = TextSendMessage(text=LineMessage)
            line_bot_api.reply_message(event.reply_token, message)

def final(keyword, all_data):
    if keyword == 'no':
        final_data = all_data
    else:
        final_data = [ keyword if i == update_list[0] else i for i in final_data]
    return final_data

if __name__ == "__main__":
    global reportData
    reportData = {}
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
