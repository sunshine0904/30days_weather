# -*- coding: utf-8 -*-
from config import *
import os
import requests
import re
import time
import datetime
from bs4 import BeautifulSoup
import xlwt
import sys

need_city_file="need_city.txt"
SLEEP_INTERVAL=1  #sleep time between two request(second)
headers = {'user-agent': UA}

#================get special city from need_city.txt===========
def formNeedCityList():
    need_city = {} 
    if os.path.exists(need_city_file) == False:
        return need_city
    f = open(need_city_file, "r", encoding="utf-8")
    for line_content in f:
        list = f.readlines()

    for i in range(0, len(list)):
        try:
            cityCode = weatherCityCode[list[i].strip()]
        except Exception as e:
            print(e,"Warning!!!!Get current city code error or current city not support now! please check need_city.txt!")
            continue
        need_city[list[i].strip()] = cityCode
    f.close()

    print("@@@@@@@@@@@@@@@@That's all the city you need:",need_city)
    return need_city


#============Get current month's history weather=============
def get_current_month_history_weather(cityid):
    start_date = datetime.datetime.now()
    mdate = "20" + datetime.date.today().strftime("%y%m")
    #base_url = "http://tianqi.2345.com/t/wea_history/js/" + str(mdate) + "/" + str(cityid) + "_" + str(mdate) + ".js"
    base_url = "http://tianqi.2345.com/wea_history/"+ str(cityid)+".htm"
    print("old data:------------",base_url)
    old_data = requests.get(base_url, headers = headers)
    if old_data.status_code != 200:
        print("Warning!!!!!!!!!!!!!!!City:%s old 15 days weather get fail.\n"%cityid)
        return None
    
    old_data_list = []
    soup = BeautifulSoup(old_data.text, "html.parser")
    table = soup.table
    tr_attr = table.find_all("tr")
    for tr in tr_attr:
        tds = tr.find_all("td")
        if len(tds) == 0:
            continue
        ymd = tds[0].get_text().encode('raw_unicode_escape').decode()[0:11]
        date = str(ymd[5:7]) + "月" + str(ymd[8:10]) + "日"
        weather_str = tds[3].get_text().encode('raw_unicode_escape').decode()
        weather = weather_str.replace("~", "转", 3)
        low_str = tds[2].get_text().encode('raw_unicode_escape').decode()
        low = low_str[0:(len(low_str) - 1)]
        high_str = tds[1].get_text().encode('raw_unicode_escape').decode()
        high = high_str[0:(len(high_str) - 1)]
        wea_item={"date":date, "status":weather, "low":low, "high":high}
        #print(wea_item)
        old_data_list.append(wea_item)
    '''
    js方式获取时使用
    pattern=r'var weather_str=(.*?),{}]'
    newPattern=re.compile(pattern,re.S)
    myAllList = re.findall(newPattern, old_data.text)[0]
    #print(myAllList)
    pattern=r"ymd:'(.*?)',bWendu:'(.*?)',yWendu:'(.*?)',tianqi:'(.*?)',fengxiang:'(.*?)',fengli:'(.*?)'"
    old_data_list = re.compile(pattern, re.S).findall(myAllList)
    #print(old_data_list)
    '''
    return old_data_list

#============Get future forty days weather=============
def get_future_40_days_weather(cityid):
    base_url="http://tianqi.2345.com/t/q.php?id=" + str(cityid)
    query = requests.get(base_url, headers=headers)
    data = query.__dict__
    if (cityid == "54401"):
        data["url"] = "http://tianqi.2345.com/zhang/54401.htm"
    
    if (cityid == "60651"):
        data["url"] = "http://tianqi.2345.com/tongshi/60651.htm"
    
    print("future data:------------",data["url"])
    forty_wea=requests.get(data["url"],headers=headers)
    if forty_wea.status_code != 200:
        print("Warning!!!!!!!!!!!!!!!City:%s future 15 days weather get fail.\n"%cityid)
        return None
    pattern=r'var fortyData=(.*?)]'
    forty_wea_str=re.findall(re.compile(pattern, re.S), forty_wea.text)[0]
    #print(forty_wea_str)
    pattern=r'"time":(.*?),"date":(.*?),"weather":"(.*?)","day_img":(.*?),"day_temp":"(.*?)","night_temp":"(.*?)"'
    forty_wea_list=re.compile(pattern, re.S).findall(forty_wea_str)
    wea_list=[]
    wea_item={}
    for cnt in range(0, len(forty_wea_list)):
        low=None
        high=None
        date=forty_wea_list[cnt][1].encode('utf-8').decode('unicode_escape')
        date=date[1:len(date)-1]
        weather=forty_wea_list[cnt][2].encode('utf-8').decode('unicode_escape')
        low=forty_wea_list[cnt][5]
        high=forty_wea_list[cnt][4]
        #print(date, weather,low,high)
        if high == "":
            continue
        if low == "":
            continue
        wea_item={"date":date, "status":weather, "low":low, "high":high}
        wea_list.append(wea_item)
    return wea_list
    
#==========write data to excel====================
def write_data_to_excel(sheet, city, row, old_data, future_data):
    sheet.write(row, 0, city)  #write city name first
    column = 1
    today = datetime.date.today()

    if old_data != None:
        for i in range(0, len(old_data)):
            '''
            mdate = time.strptime(old_data[i][0], "%Y-%m-%d")
            #jump the repeat data
            if ((mdate.tm_mday == today.day) and (mdate.tm_mon == today.month)):
                continue
            date_str = "%d月%d日"%(mdate.tm_mon, mdate.tm_mday)
            '''
            sheet.write(row, column, old_data[i]["date"])
            sheet.write(row + 1, column, old_data[i]["status"])
            sheet.write(row + 2, column, old_data[i]["low"] + u'\u2103')
            sheet.write(row + 3, column, old_data[i]["high"] + u'\u2103')
            column = column + 1
    
    if future_data!=None:
        for cnt in range(0, len(future_data)-1):
            mdate = time.strptime(future_data[cnt]["date"], "%m月%d日")
            tmp_date = "%d月%d日"%(mdate.tm_mon, mdate.tm_mday)
            #print(tmp_date, old_data[len(old_data) - 1]["date"])
            if (tmp_date == old_data[len(old_data) - 1]["date"]):
                continue
            sheet.write(row, column, tmp_date)
            sheet.write(row + 1, column, future_data[cnt]["status"])
            sheet.write(row + 2, column, future_data[cnt]["low"] + u'\u2103')
            sheet.write(row + 3, column, future_data[cnt]["high"] + u'\u2103')
            column = column + 1


def main():
    print("^_^^_^^_^Usage:add city name to need_city.txt. if need_city.txt is empty,get all city.")
    
    #record the start time
    start_date=datetime.datetime.now()
    dt = time.strptime(str(start_date)[0:19], '%Y-%m-%d %H:%M:%S')
    file_name_str = "%s%s%s_%s%s_weather.xls"%(str(dt.tm_year), str(dt.tm_mon), str(dt.tm_mday), str(dt.tm_hour), str(dt.tm_min)) 

    #create excel and add sheet to save data
    result= xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = result.add_sheet('result', cell_overwrite_ok=True)
    cityRow=0
    cnt=1
    
    #get the city from need_city.txt
    need_city = formNeedCityList()
    #if need city is empty, then get all the city
    if len(need_city) == 0:
        need_city = weatherCityCode
        print("need city list is empty!Get all city data.")

    #start get data and write to sheet
    for key,val in need_city.items():
        print(str(time.strftime('%Y.%m.%d-%H:%M:%S'))+"--------%d--------------%s--%s-------------"%(cnt,key,val))
        old_data = get_current_month_history_weather(val)
        future_data=get_future_40_days_weather(val)
        print(str(time.strftime('%Y.%m.%d-%H:%M:%S'))+"--------%d--------------%s--%s-------------\n"%(cnt,key,val))
        sys.stdout.flush()
        if len(old_data)==0 and len(future_data) == 0:
            continue
        write_data_to_excel(sheet, key, cityRow, old_data, future_data)
        cityRow = cityRow + 4
        result.save(file_name_str)
        cnt+=1
        time.sleep(SLEEP_INTERVAL)
    
    #save data
    result.save(file_name_str)

    #print cost time
    end_date=datetime.datetime.now()
    print("\n",end_date - start_date,"(^_^)(^_^)(^_^)All city weather data get success!\n")

main()
