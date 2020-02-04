# -*- coding: utf-8 -*-
from config import *
import os
import requests
import re
import time
import datetime
from bs4 import BeautifulSoup
import xlwt

MYCOUNT=0
# =============得到城市和对应的编码，这个开始运行，把数据保存到 config.py文件中，以后就不用运行了 这个数据是死的，一般不会变
def getCityCodeAjax(Mcount=MYCOUNT):
    global MYCOUNT
    try:
        # query = {'app': 'shopsearch', 'ie': '	utf8',
        #          }
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
            # pattern =''
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
    if os.path.exists("need_city.txt") == False:
        return None
    need_city = {} 
    f = open("need_city.txt", "r", encoding="utf-8")
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
    base_url = "http://tianqi.2345.com/t/wea_history/js/202002/" + str(cityid) + "_" + str(mdate) + ".js"
    print("old data:------------",base_url)
    old_data = requests.get(base_url, headers = headers)
    if old_data.status_code != 200:
        print("Warning!!!!!!!!!!!!!!!City:%s old 15 days weather get fail.\n"%cityid)
        return None
    
    pattern=r'var weather_str=(.*?),{}]'
    newPattern=re.compile(pattern,re.S)
    myAllList = re.findall(newPattern, old_data.text)[0] #得到完整的就送格式数据
    pattern=r"ymd:'(.*?)',bWendu:'(.*?)',yWendu:'(.*?)',tianqi:'(.*?)',fengxiang:'(.*?)',fengli:'(.*?)'"
    old_data_list = re.compile(pattern, re.S).findall(myAllList)
    #print(old_data_list)
    return old_data_list



#===========获取未来15天天气===========
def get_future_15_days_weather(cityid):
    headers = {'user-agent': UA}
    base_url="http://tianqi.2345.com/t/q.php?id=" + str(cityid)
    query = requests.get(base_url, headers=headers)
    data = query.__dict__
    print("future data:------------",data["url"])
    day15_wea=requests.get(data["url"],headers=headers)
    #获取数据失败
    if day15_wea.status_code != 200:
        print("Warning!!!!!!!!!!!!!!!City:%s future 15 days weather get fail.\n"%cityid)
        return None
    res=BeautifulSoup(day15_wea.content, "lxml")
    wea_list=[]
    wea_item={}
    
    #day7=res.find_all(id="day7info")[0].find_all(class_="clearfix has_aqi")[0].find_all(class_="week-detail-now")
    day7=res.find_all(id="day7info")[0].find_all("ul")[0].find_all(class_="week-detail-now")
    day7.append(res.find_all(id="day7info")[0].find_all("ul")[0].find_all(class_="week-detail-now lastd"))
    for cnt in range(0, len(day7)-1):
        mdate=day7[cnt].find("strong").get_text().strip()
        status=day7[cnt].b.string
        low=day7[cnt].i.find(class_="blue").string
        high=day7[cnt].i.find(class_="red").string
        wea_item={"date":mdate[0:6],"status":status,"low":low,"high":high}
        wea_list.append(wea_item)
        #print(mdate[0:7], status, low, high)
    
    #TODO:增加lastd天气 
    day8=res.find_all("ul","li",class_="clearfix has_aqi has_aqi_wind")
    for cnt in range(0,len(day8[0].find_all("li"))-1):
        current=day8[0].find_all("li")[cnt]
        mdate=current.find("strong").get_text().strip()
        status=current.b.string
        low=current.i.find(class_="blue").string
        high=current.i.find(class_="red").string
        #print(mdate[0:7],status,low,high)
        wea_item={"date":mdate[0:6],"status":status,"low":low,"high":high}
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
            sheet.write(row + 3, column, future_data[cnt]["high"])
            #sheet.write(row + 3, column, future_data[cnt]["high"] + u'\u2103')
            column = column + 1


#得到一个城市 给定日期范围的 所有天气数据
def main():
    print("^_^^_^^_^Usage:add city name to need_city.txt. if need_city.txt is empty,get all city.")
    #记录开始时间
    start_date=datetime.datetime.now()

    #删除老的数据
    if os.path.exists("30days_weather.xls"):
        os.remove("30days_weather.xls")
        print("remove old 30days_weather.xls file success.............")

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
        print("%d--------------%s--%s-------------"%(cnt,key,val))
        old_data = get_old_15_days_weather(val)
        future_data=get_future_15_days_weather(val)
        print("%d--------------%s--%s-------------\n"%(cnt,key,val))
        if old_data==None and future_data == None:
            continue
        write_data_to_excel(sheet, key, cityRow, old_data, future_data)
        cityRow = cityRow + 4
        result.save(r'./30days_weather.xls')
        cnt+=1
        time.sleep(0.5)
    
    #获取结束保存数据
    result.save(r'./30days_weather.xls')

    #输出获取资源消耗的时间
    end_date=datetime.datetime.now()
    print("\n",end_date - start_date,"(^_^)(^_^)(^_^)All city weather data get success!\n")

main()
