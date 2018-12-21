# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-508930171334-506974132673-O5cWPdkLOjOPBzfCZ3QCRZVw"
slack_client_id = "508930171334.507471678675"
slack_client_secret = "4ac768a4aef765038206ade43332a645"
slack_verification = "sT6FxlOhGXZVps5vTZn2sfet"
sc = SlackClient(slack_token)

total_ch_info=[]

priority_title =[]
priority_gage =[]

def removeSpacebarAndSign(str):
    strSpl=[]
    result=""
    strSpl = str.split()
    for s in strSpl:
        result+=s
    if "(" in result:
        result = result[:result.find("(")]
    return result

def get_time_table_from_sk_all(url):
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = {}
    for i, keyword in enumerate(soup.find_all("li", class_="list")):
        tvStr = keyword.get_text()[:61].strip()
        tvStr = tvStr.replace("\n", "|")
        if "||" in tvStr:
            tvStr = tvStr.replace("||", "")
        tvStr=tvStr.strip()
        tvInfo =tvStr.split("|")
        #keywords에 해당 key값이 있다면 추가로 더해주고 없다면 넣는다.
        removeSpace = removeSpacebarAndSign(tvInfo[1])
        if removeSpace in keywords.keys():
            keywords[removeSpace].append(tvInfo[1])
            keywords[removeSpace].append(tvInfo[0])
        else:
            keywords[removeSpace]=[tvInfo[1], tvInfo[0]]

    return keywords
##################################################
def get_time_table_from_sk_time(url,time):
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []
    for i, keyword in enumerate(soup.find_all("li", class_="list")):
        tvStr = keyword.get_text()[:61].strip()
        tvStr = tvStr.replace("\n", " | ")

        if " |  | " in tvStr:
            tvStr = tvStr.replace(" |  | ", "")
            tvStr += "  <-- 현재 상영중"
        if time<=tvStr[:5]:
            keywords.append(tvStr)
    return keywords

def get_time_table_from_sk(url):
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []
    for i, keyword in enumerate(soup.find_all("li", class_="list")):
        tvStr = keyword.get_text()[:61].strip()
        tvStr = tvStr.replace("\n", " | ")

        if " |  | " in tvStr:
            tvStr = tvStr.replace(" |  | ", "")
            tvStr += "  <-- 현재 상영중"
        keywords.append(tvStr)
    return keywords

#################################################################################
#이 부분은 프로그램 시작과 동시에 채널 정보를 크롤링해와서 저장 합니다.
keywords = []
url = "http://m.skbroadband.com/content/realtime/Channel_List.do"
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=12&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=11&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=13&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=15&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=70&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=63&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=241&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=242&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=243&key_depth3="
keywords += [get_time_table_from_sk_all(url)]
################################################################################
total_ch_info=keywords

def search_first_priority(titlelist, title):
    orititle = ''
    starttime = ''
    max_priority = 0
    for i, titleinlist in enumerate(titlelist):
        if i % 2 == 0:
            tmp = titleinlist.lower()
            tmp = tmp.replace(" ", '')
            if title in tmp:
                priority_title.append(titleinlist)
                priority_gage.append(len(title) / len(tmp))
                if len(title) / len(tmp) > max_priority:
                    orititle = titleinlist
                    starttime = titlelist[i+1]
                    max_priority = len(title) / len(tmp)

    return orititle, starttime

def search_by_title(bc, title):
    idx = -1
    orititle = ''
    starttime= ''
    if bc.lower() == 'sbs':
        idx = 0
    elif bc.lower() == 'kbs2':
        idx = 1
    elif bc.lower() == 'kbs1':
        idx = 2
    elif bc.lower() == 'mbc':
        idx = 3
    elif bc.lower() == 'ebs':
        idx = 4
    elif bc.lower() == 'obs':
        idx = 5
    elif bc.lower() == 'ebs2':
        idx = 6
    elif bc.lower() == 'jtbc':
        idx = 7
    elif bc.lower() == 'mbn':
        idx = 8
    elif bc.lower() == '채널a':
        idx = 9
    elif bc.lower() == 'tvchosun':
        idx = 10

    if title in total_ch_info[idx] != None:
        titlelist = total_ch_info[idx].get(title)
        if len(titlelist) < 3:
            orititle = titlelist[0]
            starttime = titlelist[1]
        else:
            orititle, starttime = search_first_priority(titlelist, title)
    else:
        maxpriority = -1
        keylist = total_ch_info[idx].keys()
        for i in keylist:
            titlelist = total_ch_info[idx].get(i)
            nowtitle, nowtime = search_first_priority(titlelist, title)
            if len(nowtitle) != 0 and  (len(title) / len(nowtitle.lower().replace(" ", ""))) > maxpriority:
                orititle = nowtitle
                starttime = nowtime
                maxpriority = len(title) / len(orititle.lower().replace(" ", ""))

    return orititle, starttime

# 크롤링 함수 구현하기
def command_split(text):
    ######################################명령어 분할 : ex) 'SBS 황후의 품격' -> 'SBS', '황후의품격'
    title = ""
    bc = ""
    text = text.lower()
    for i, word in enumerate(text.split()):
        if i == 1:
            bc = word
        elif i > 1:
            title += word

    return bc, title

def get_time_table_from_sk(url):
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []
    for i, keyword in enumerate(soup.find_all("li", class_="list")):
        tvStr = keyword.get_text()[:61].strip()
        tvStr = tvStr.replace("\n", " | ")

        if " |  | " in tvStr:
            tvStr = tvStr.replace(" |  | ", "")
            tvStr += "  <-- 현재 상영중"
        keywords.append(tvStr)
    return keywords

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    ######################################정규방송#####################################
    # 여기에 함수를 구현해봅시다.
    text = text.lower()

    keywords = []

    bc, title = command_split(text)
    ti =''
    st=''
            # print(len(title))
    if len(title)==0:
        if "sbs" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do"
            keywords = get_time_table_from_sk(url)
        elif "kbs2" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=12&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "kbs1" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=11&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "mbc" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=13&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "ebs" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=15&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "obs" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=70&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "ebs2" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=63&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "jtbc" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "mbn" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=241&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "체널a" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=242&key_depth3="
            keywords = get_time_table_from_sk(url)
        elif "tvchosun" in text:
            url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=243&key_depth3="
            keywords = get_time_table_from_sk(url)
        else:
            keywords.append("안녕하세요. 방송 편성 알리미입니다.\n"
                            + "sbs, kbs2, kbs1, mbc, ebs, obs, ebs2, jtbc, mbn, 채널a, tvchosun"
                            + "에 대한 정보를 드립니다.\n"
                            + "1. 전체 방송 편성표에 대한 정보를 원하시면"
                            + "방송국명(위에 나열한 이름과 같이 써주세요)\n"
                            + "2. 특정 시간 이후 방송 편성표에 대한 정보를 원하시면"
                            + "방송국명(위에 나열한 이름과 같이 써주세요) 시간(00:00방식)\n"
                            + "3. 특정 방송국 프로그램에 대한 시간 정보를 원하시면"
                            + "방송국명(위에 나열한 이름과 같이 써주세요) 프로그램명\n"
                            + "방식으로 써주세요"
                            )
    else:
        regex = re.compile(r'\d\d:\d\d')
        mo = regex.search(title)
        if mo != None:
            time=mo.group()
            if "sbs" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do"
                keywords = get_time_table_from_sk_time(url,time)
            elif "kbs2" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=12&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "kbs1" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=11&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "mbc" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=13&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "ebs" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=15&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "obs" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=70&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "ebs2" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=5100&key_depth2=63&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "jtbc" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "mbn" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=241&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "체널A" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=242&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
            elif "tv chosun" in text:
                url = "http://m.skbroadband.com/content/realtime/Channel_List.do?key_depth1=7800&key_depth2=243&key_depth3="
                keywords = get_time_table_from_sk_time(url,time)
        else:
            ti, st = search_by_title(bc, title)
            font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
            plt.rcParams.update({'font.size': 7})
            rc('font', family=font_name)
            plt.bar(priority_title, priority_gage)
            plt.xlabel('프로그램명')
            plt.ylabel('유사도')
            plt.title('유사도 막대 그래프')

            plt.show()
                    # for i, keyword in enumerate(soup.find_all("p",class_="artist")):
            # if i < 10:
            # tmp = str(i + 1) + "위 : "
            # keywords[i] += "/"+ keyword.get_text().strip()

            # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
            if len(ti) > 0:
                keywords.append(ti + ' | ' + st)
    #keywords.append(title)
    for i in range(0, len(priority_gage)):
        print(priority_title[i] + " = " + str(priority_gage[i]))
    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)