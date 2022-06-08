import os
import requests
import random
import pickle
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

# Line Chatbot App    
app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('dcShAnTSdAJ0WOWZZsiM/CMj6VOk1ZFax6qlmxpIY694mYZaDVLwFnbjQydrhTXHjKsZSQ27fgnBdHGpuYPHrGJLIuaSHqqbiBweVJV9y+u+LLxT6mrL4Mv10ZLI7+UtDdutfRJ6OdEU1+1Tb+CJRwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('aae43f30fd63fad915e19af197b4e147')

# 星座列表清單
signs_dict = {"水瓶":"Aquarius", "雙魚":"Pisces", "牡羊":"Aries", 
            "金牛":"Taurus", "雙子":"Gemini", "巨蟹":"Cancer", 
            "獅子":"Leo", "處女":"Virgo", "天秤":"Libra", 
            "天蠍":"Scorpio", "射手":"Sagittarius", "摩羯":"Capricorn"}

signs = signs_dict.keys()
numbered_signs = dict(zip(range(0, len(signs)), signs))


def get_all_holoscopes():
    # my_sign = input("請輸入你的星座（兩個字)：")
    url_head = "http://www.daily-zodiac.com/zodiac/"
    htmls = []

    for sign in signs_dict.values(): 
        url = url_head + sign
        # print(url)
        
        html = requests.get(url).text
        htmls.append(html)

    # print(len(htmls))

    soups = []
    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser')
        soups.append(soup)

    holoscopes = []
    for soup in soups:
        holoscope = soup.find_all("meta", property="og:description")[0]['content']
        # print(trend)
        holoscopes.append(holoscope)

    all_holoscopes = dict(zip(signs_dict.keys(), holoscopes))
    return all_holoscopes


# 監聽所有來自 /callback 的 Post Request
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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    all_holoscopes = get_all_holoscopes()
    example_sign = numbered_signs[random.randint(0, len(signs))]
    received_message = TextSendMessage(text=event.message.text)
    # print(message.text)
    try:
        reply_message = TextSendMessage(text=f"{received_message.text}座的你，{all_holoscopes[received_message.text]}")
        line_bot_api.reply_message(event.reply_token, reply_message)

    except:
        reply_message = TextSendMessage(text=f"如果想知道今日星座運勢，請輸入你星座的前兩字（例如：{example_sign}）唷～")
        line_bot_api.reply_message(event.reply_token, reply_message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)