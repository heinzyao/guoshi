import requests
import pickle
import pymysql
import time
import base64
from datetime import datetime
from bs4 import BeautifulSoup

ts = time.time()
dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

signs_dict = {"水瓶":"Aquarius", "雙魚":"Pisces", "牡羊":"Aries", 
            "金牛":"Taurus", "雙子":"Gemini", "巨蟹":"Cancer", 
            "獅子":"Leo", "處女":"Virgo", "天秤":"Libra", 
            "天蠍":"Scorpio", "射手":"Sagittarius", "摩羯":"Capricorn"}

def get_all_holoscopes():
    url_head = "http://www.daily-zodiac.com/zodiac/"

    htmls = []
    for sign in signs_dict.values(): 
        url = url_head + sign
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
        holoscopes.append(holoscope)

    all_holoscopes = dict(zip(signs_dict.keys(), holoscopes))

    return all_holoscopes

def upload_data(data):
    with open("pw.pkl", "rb") as f:
        pw = base64.b64decode(pickle.load(f)).decode('utf-8')
    
    db = pymysql.connect(host="localhost",user="root",passwd=pw ,database="holoscopes")
    cursor = db.cursor()
    
    sql = "INSERT INTO daily_holoscopes(sign, holoscopes, date, weekday) \
        VALUES (%s, %s, %s, %s)"

    try:
        cursor.executemany(sql, data)
        db.commit()

    except Exception as e:
        print(e)
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    all_holoscopes = get_all_holoscopes()
    data = tuple(i + tuple([dt]) + tuple([datetime.today().weekday()]) for i in all_holoscopes.items())
    print(data)
    upload_data(data)