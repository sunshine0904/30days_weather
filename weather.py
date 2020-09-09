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
#休眠时间
SLEEP_INTERVAL=1
MYCOUNT=0

# =============得到城市和对应的编码，这个开始运行，把数据保存到 config.py文件中，以后就不用运行了 这个数据是死的，一般不会变
def getCityCodeAjax(Mcount=MYCOUNT):
    global MYCOUNT
    try:
        # query = {'app': 'shopsearch', 'ie': '	utf8',}
        requestFirst = 'http://tianqi.2345.com/js/citySelectData.js'
        headers = {'user-agent': UA}
        try:
            r = requests.get(requestFirst, headers=headers)
        except Exception as e:
            print(e,'error')

        #print(r.status_code, r.url)
        if r.status_code == 200:
            # print(r.text)
            pattern=r'var prov=new Array.*?台湾-36\'.*?(.*?)var provqx'
            newPattern=re.compile(pattern,re.S)
            myAllList = re.findall(newPattern, r.text)[0] #得到完整的就送格式数据
            # print(len(myAllList),type(myAllList), myAllList)
            secondP="'(.*?)'"
            # secondP=r"ymd:'(.*?)',bWendu:'(.*?)',yWendu:'(.*?)',tianqi:'(.*?)',fengxiang:'(.*?)',fengli:'(.*?)'"
            newList=re.compile(secondP, re.S).findall(myAllList)
            # print(len(newList),newList)
            #print('===============================')
            return newList
        else:
            print('得到城市和对应编码错误')
            return None
    except Exception as e:
        MYCOUNT+=1
        print(e,'第\t%d次\t请求链接出现问题，正在请求下一次链接......'%MYCOUNT)
        if MYCOUNT<6:
            getCityCodeAjax(Mcount=MYCOUNT)
        else:
            MYCOUNT = 0
            return None


# ============处理城市和对应编码数据，变成一个字典，存放到 config.py文件中，开始运行，以后不需要了======
def cityCodeList(cityCodeList=getCityCodeAjax()):
    allDict={}
    outersingleListCity=[]
    outersingleListCode=[]
    for city in cityCodeList:
        print(city)
        everyCityList=city.split('|')
        singleListCity=[]
        singleListCode=[]
        for mycity in everyCityList:
            try:
                singleCity=mycity.split(' ')[1]
                singleListCity.append(singleCity.split('-')[0])
                singleListCode.append(singleCity.split('-')[1])
                outersingleListCity+=singleListCity
                outersingleListCode+=singleListCode
            except Exception as e:
                print(e,'-------处理城市和编码时 error-----------------')
                continue
    #print(len(outersingleListCode),outersingleListCode)
    # allDict=dict(zip(outersingleListCity,outersingleListCode))
    allDict = dict(zip( outersingleListCode,outersingleListCity))
    print(len(allDict),type(allDict),allDict)
    return allDict

#================从need_city.txt中获取需要的城市列表===========
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
            print(e,"Warning!!!!获取当前城市代码错误......请检查城市名称或者当前城市不支持")
            continue
        need_city[list[i].strip()] = cityCode
    f.close()

    print("@@@@@@@@@@@@@@@@需要获取天气的城市：",need_city)
    return need_city
    



#============获取之前数天的天气=============
def get_old_15_days_weather(cityid):
    headers = {'user-agent': UA}
    start_date = datetime.datetime.now()
    mdate = "20" + datetime.date.today().strftime("%y%m")
    base_url = "http://tianqi.2345.com/t/wea_history/js/" + str(mdate) + "/" + str(cityid) + "_" + str(mdate) + ".js"
    print("old data:------------",base_url)
    old_data = requests.get(base_url, headers = headers)
    if old_data.status_code != 200:
        print("Warning!!!!!!!!!!!!!!!City:%s old 15 days weather get fail.\n"%cityid)
        return None
    
    pattern=r'var weather_str=(.*?),{}]'
    newPattern=re.compile(pattern,re.S)
    myAllList = re.findall(newPattern, old_data.text)[0] #得到完整的就送格式数据
    #print(myAllList)
    pattern=r"ymd:'(.*?)',bWendu:'(.*?)',yWendu:'(.*?)',tianqi:'(.*?)',fengxiang:'(.*?)',fengli:'(.*?)'"
    old_data_list = re.compile(pattern, re.S).findall(myAllList)
    #print(old_data_list)
    return old_data_list

#============获取未来40天的天气=============
def get_future_40_days_weather(cityid):
    headers = {'user-agent': UA}
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
    
#==========写数据====================
def write_data_to_excel(sheet, city, row, old_data, future_data):
    sheet.write(row, 0, city)  #写当前城市名
    column = 1
    today = datetime.date.today()

    if old_data != None:
        for i in range(len(old_data)):
            mdate = time.strptime(old_data[i][0], "%Y-%m-%d")
            #过去的天气中包含当天的天气会导致当前天气重复
            if ((mdate.tm_mday == today.day) and (mdate.tm_mon == today.month)):
                continue
            date_str = "%d月%d日"%(mdate.tm_mon, mdate.tm_mday)
            sheet.write(row, column, date_str)
            sheet.write(row + 1, column, old_data[i][3])
            sheet.write(row + 2, column, old_data[i][2])
            sheet.write(row + 3, column, old_data[i][1])
            column = column + 1
    
    if future_data!=None:
        for cnt in range(0, len(future_data)-1):
            mdate = time.strptime(future_data[cnt]["date"], "%m月%d日")
            sheet.write(row, column, "%d月%d日"%(mdate.tm_mon, mdate.tm_mday))
            sheet.write(row + 1, column, future_data[cnt]["status"])
            sheet.write(row + 2, column, future_data[cnt]["low"] + u'\u2103')
            sheet.write(row + 3, column, future_data[cnt]["high"] + u'\u2103')
            column = column + 1


#得到一个城市 给定日期范围的 所有天气数据
def main():
    print("^_^^_^^_^Usage:add city name to need_city.txt. if need_city.txt is empty,get all city.")
    
    #记录开始时间
    start_date=datetime.datetime.now()
    dt = time.strptime(str(start_date)[0:19], '%Y-%m-%d %H:%M:%S')
    file_name_str = "%s%s%s_%s%s_weather.xls"%(str(dt.tm_year), str(dt.tm_mon), str(dt.tm_mday), str(dt.tm_hour), str(dt.tm_min)) 

    #创建数据表格
    result= xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = result.add_sheet('result', cell_overwrite_ok=True)
    cityRow=0
    cnt=1
    
    #构建需要获取的城市列表
    need_city = formNeedCityList()
    #如果需要获取的城市列表为空则默认获取所有城市
    if len(need_city) == 0:
        need_city = weatherCityCode
        print("need city list is empty!Get all city data.")

    #开始获取数据并写入表格
    for key,val in need_city.items():
        print(str(time.strftime('%Y.%m.%d-%H:%M:%S'))+"--------%d--------------%s--%s-------------"%(cnt,key,val))
        old_data = get_old_15_days_weather(val)
        #future_data=get_future_15_days_weather(val)
        future_data=get_future_40_days_weather(val)
        print(str(time.strftime('%Y.%m.%d-%H:%M:%S'))+"--------%d--------------%s--%s-------------\n"%(cnt,key,val))
        sys.stdout.flush()
        if old_data==None and future_data == None:
            continue
        write_data_to_excel(sheet, key, cityRow, old_data, future_data)
        cityRow = cityRow + 4
        result.save(file_name_str)
        cnt+=1
        time.sleep(SLEEP_INTERVAL)
    
    #获取结束保存数据
    result.save(file_name_str)

    #输出获取资源消耗的时间
    end_date=datetime.datetime.now()
    print("\n",end_date - start_date,"(^_^)(^_^)(^_^)All city weather data get success!\n")


main()
