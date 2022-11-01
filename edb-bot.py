import json
import telebot
import requests
from bs4 import BeautifulSoup
import cloudscraper
import math
from keyboa import Keyboa


with open("key.txt", "r") as f:
    API_key =f.read()
bot = telebot.TeleBot(API_key)
cache = [""] #cache of user results
cached_keyword = ""


@bot.message_handler(commands=['start','help'])
def start(message):
    print("Start message from "+str(message.from_user.id)+" - " + message.text)
    bot.send_message(message.from_user.id,"Enter search text")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print("message from "+str(message.from_user.id)+" - " + message.text)
    answerMsg(message.text, message.from_user.id)
    #bot.send_message(message.from_user.id, searchExploit(message), parse_mode="html")
    #return

def answerMsg(text, user_id):
    #if True:
    try:
        answer = searchExploit(text)
        btns = []
        if len(answer)>1:
            if answer[2]>1:
                i = 0
                print(type(answer[1]))
                if answer[1] > 1:
                    btns.append({'text': '< Page '+str(answer[1]-1), 'callback_data': text.split('|')[0]+"|"+str(answer[1]-1)})
                    i +=1
                if answer[1] < answer[2]:
                    btns.append({'text': 'Page '+str(answer[1]+1)+' >', 'callback_data': text.split('|')[0]+"|"+str(answer[1]+1)})
                    i +=1
                kb_btns = Keyboa(items=btns, items_in_row=i)
                bot.send_message(user_id, answer[0], parse_mode="html", reply_markup = kb_btns())
                return
    #try:
        bot.send_message(user_id, answer[0], parse_mode="html")
    except:
        bot.send_message(user_id, "Something went wrong")
@bot.callback_query_handler(func=lambda call: True)
def test_callback(call): # <- passes a CallbackQuery type object to your function
    print(call.data)
    answerMsg(str(call.data), call.from_user.id)


def get_from_cache(page_num):
    global cache
    if len(cache) ==0:
        return ["No records found"]
    if (page_num<1) | ((len(cache)-(page_num-1)*10)<1):
        page_num=1
    i=0
    total = math.ceil(len(cache)/10)
    results = f"Page {page_num} of {total}\n\n"
    for element in cache[(page_num-1)*10:] :
        if (len(results)+len(element))>4095:
            return results
        results += element
        i +=1
        if i > 9:
            return [results,page_num,total]
    return [results,page_num,total]




def searchExploit(searchTxt):
    global cached_keyword
    global cache
    page_num = 1
    if len(searchTxt.split("|"))>1 :
        if  searchTxt.split("|")[1].isnumeric() :
            page_num = int(searchTxt.split("|")[1])
    searchstr = searchTxt.split("|")[0].strip()
    if searchstr=="":
        return ["No records found"]
    results = ""
    if (searchstr == cached_keyword) :
        return get_from_cache(page_num)
    URL = f"https://www.exploit-db.com/search?q={searchstr}&platform=windows"
    scraper = cloudscraper.create_scraper(delay=10,   browser={'custom': 'ScraperBot/1.0',})
    page = scraper.get(URL)
    URL = f"https://exploit-db.com/search?text={searchstr}&platform=windows&draw=2"
    exploit_json = json.loads(requests.get(URL, headers={"Accept" : "application/json, text/javascript, */*", "X-Requested-With": "XMLHttpRequest"}, cookies={
    "XSRF-TOKEN" : page.cookies.get("XSRF-TOKEN")}).text)
    total = exploit_json.get("recordsTotal")
    print(total)
    if total==0:
        return ["No records fond"]
    cached_keyword = searchstr
    cache.clear()
    i = 0
    for element in exploit_json.get("data") :
        downLink = "<a href='https://exploit-db.com"+BeautifulSoup(element.get("download"),"html.parser").find("a")["href"]+"'>download</a>"
        new_element = element.get("id") + " - " + element.get("description")[1] + " " + downLink + "\n\n"
        cache.append(new_element)
    return get_from_cache(page_num)

#print(superuser("smb"))
bot.polling(none_stop=True, interval=0)