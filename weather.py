# -*- coding: utf-8 -*-
from config import *
import os
import requests
import re
import  time
from multiprocessing import Pool
import datetime
from bs4 import BeautifulSoup
import xlwt

# http://tianqi.2345.com/t/wea_history/js/57083_20129.js
# http://tianqi.2345.com/t/wea_history/js/57083_201209.js

MYCOUNT=0
# =================得到每月的天气数据===============
def getEveryMonthWeatherList(cityCode,date,Mcount=MYCOUNT):
    global MYCOUNT
    try:
        # query = {'app': 'shopsearch', 'ie': '	utf8',
        #          }
        dateFirst = str(date.split('-')[0])+ str(int(date.split('-')[1]))
        dateTwo=str(date.split('-')[0])+str(date.split('-')[1])
        requestFirst = 'http://tianqi.2345.com/t/wea_history/js/{}_{}.js'.format(cityCode,dateFirst)
        requestTwo = 'http://tianqi.2345.com/t/wea_history/js/{}/{}_{}.js'.format(dateTwo,cityCode, dateTwo)
        headers = {'user-agent': UA}
        try:
            r = requests.get(requestFirst, headers=headers)
            if r.status_code != 200:
                # print( '老地址出错了，请求新地址')
                r = requests.get(requestTwo, headers=headers)
        except Exception as e:
            print(e,'error')
        print("old dadta:---------",r.status_code, r.url)
        if r.status_code == 200:
            # print(r.text)
            # print(r.headers)

            pattern=r'var weather_str=(.*?),{}]'
            newPattern=re.compile(pattern,re.S)
            myAllList = re.findall(newPattern, r.text)[0] #得到完整的就送格式数据
            secondP=r"ymd:'(.*?)',bWendu:'(.*?)',yWendu:'(.*?)',tianqi:'(.*?)',fengxiang:'(.*?)',fengli:'(.*?)'"
            newList=re.compile(secondP, re.S).findall(myAllList)
            # print(len(newList),newList)
            # print(type(newList))
            return newList
        else:
            print('可能输入日期有误')
            return None

    except Exception as e:
        MYCOUNT+=1
        print(e,'第\t%d次\t请求链接出现问题，正在请求下一次链接......'%MYCOUNT)
        #对于一些无法预料的错误的处理 比如淘宝不让搜索 sisy私服 这个，如果不加判断条件，程序就会一直请求，死循环了
        if MYCOUNT<6:
            getEveryMonthWeatherList(cityCode, date, Mcount=MYCOUNT)
        else:
            MYCOUNT = 0
            print('出错次数达到上限，程序结束，请检查函数 ')
            return None

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

        print(r.status_code, r.url)
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
            #print(type(newList))
            return newList
        else:
            print('得到城市和对应编码错误')
            return None
    except Exception as e:
        MYCOUNT+=1
        print(e,'第\t%d次\t请求链接出现问题，正在请求下一次链接......'%MYCOUNT)
        #对于一些无法预料的错误的处理 比如淘宝不让搜索 sisy私服 这个，如果不加判断条件，程序就会一直请求，死循环了
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
    print(len(outersingleListCode),outersingleListCode)
    # allDict=dict(zip(outersingleListCity,outersingleListCode))
    allDict = dict(zip( outersingleListCode,outersingleListCity))
    print(len(allDict),type(allDict),allDict)
    return allDict


# =================得到一个城市给定日期范围的 所有天气数据列表=================
def manyDateDataList(cityCode):
    try:
        dateList = createDateList(startDate,endDate)
        bigDataList = []
        for date in dateList:
            try:
                smallList=getEveryMonthWeatherList(cityCode, date)
                print(smallList)
                bigDataList += smallList
            except Exception as e:
                print(e, 'error')
                continue
            time.sleep(1)
        print(len(bigDataList),bigDataList)
        return bigDataList
    except Exception as e:
        print(e)

# ======================得到类似 ['2012-01', '2012-02', '2012-03']===========
def createDateList(startDate,endDate):
    try:
        yearList = [year for year in range(int(startDate.split('-')[0]),int(endDate.split('-')[0])+1)]
        print(yearList)
        # yearList=['2012','2013','2014','2015','2016']
        # yearList = ['2012', '2013']
        monthList=['01','02','03','04','05','06','07','08','09','10','11','12']
        allDateList=[]
        startYear=int(startDate.split('-')[0])
        startMonth = int(startDate.split('-')[1])
        for year in yearList:
            tempList=[]
            # 保证第一年的起始月是对的
            if year==startYear:
                newMonthList=monthList[startMonth-1:]
            else:
                newMonthList=monthList

            for month in newMonthList:
                yearMonth='{}-{}'.format(year,month)
                tempList.append('{}-{}'.format(year,month))
                if endDate == yearMonth:
                    break #结束本轮里层的 for循环，下面的循环不在执行，但外的循环还是继续执行
            allDateList+=tempList
        print(len(allDateList),allDateList)
        return allDateList
    except Exception as e:
        print(e,'创建日期列表出错了,这里只查询了 开始和结束日期....')
        return [startDate,endDate]


# ===================从城市名字获取城市代码================
def fromCityGetCityCode(needCityList):
    cityCodeLs=[]
    try:
        for curCity in needCityList:
            try:
                # weatherCityCode 是一个字典 在config.py文件中，存放城市和编码的字典
                cityCode = weatherCityCode[curCity]
                cityCodeLs.append(cityCode)
            except Exception as e:
                print(e,'得到城市代码错误...')
                continue
        print(len(cityCodeLs),cityCodeLs)
        return cityCodeLs
    except Exception as e:
        print(e,'从城市名字获取城市编码出错了')
        return None

#===========获取未来15天天气===========
def get_future_15_days_weather(cityid):
    headers = {'user-agent': UA}
    base_url="http://tianqi.2345.com/t/q.php?id=" + str(cityid)
    query = requests.get(base_url, headers=headers)
    data = query.__dict__
    print("future data:------------",base_url, data["url"])
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
        mdate=day7[cnt].find("strong").get_text()
        status=day7[cnt].b.string
        low=day7[cnt].i.find(class_="blue").string
        high=day7[cnt].i.find(class_="red").string
        wea_item={"date":mdate[0:7],"status":status,"low":low,"high":high}
        wea_list.append(wea_item)
        #print(mdate[0:7], status, low, high)
    
    #TODO:增加lastd天气 
    day8=res.find_all("ul","li",class_="clearfix has_aqi has_aqi_wind")
    for cnt in range(0,len(day8[0].find_all("li"))-1):
        current=day8[0].find_all("li")[cnt]
        mdate=current.find("strong").get_text()
        status=current.b.string
        low=current.i.find(class_="blue").string
        high=current.i.find(class_="red").string
        #print(mdate[0:7],status,low,high)
        wea_item={"date":mdate[0:7],"status":status,"low":low,"high":high}
        wea_list.append(wea_item)
    return wea_list

#==========写数据====================
def write_data_to_excel(sheet, city, row, old_data, future_data):
    sheet.write(row, 0, city)  #写当前城市名
    column = 1
	
    if old_data != None:
        for i in range(len(old_data)):
            sheet.write(row, column, old_data[i][0])
            sheet.write(row + 1, column, old_data[i][3])
            sheet.write(row + 2, column, old_data[i][2])
            sheet.write(row + 3, column, old_data[i][1])
            column = column + 1
	
    if future_data!=None:
        for cnt in range(0, len(future_data)-1):
            sheet.write(row, column, future_data[cnt]["date"])
            sheet.write(row + 1, column, future_data[cnt]["status"])
            sheet.write(row + 2, column, future_data[cnt]["low"] + u'\u2103')
            sheet.write(row + 3, column, future_data[cnt]["high"])
            #sheet.write(row + 3, column, future_data[cnt]["high"] + u'\u2103')
            column = column + 1


#=========== 主函数===================
def main():
    #得到一个城市 给定日期范围的 所有天气数据
    #cityInfoList= manyDateDataList(cityCode)
    start_date=datetime.datetime.now()
    if os.path.exists("30days_weather.xls"):
        os.remove("30days_weather.xls")
        print("remove old 30days_weather.xls file success.............")
    result= xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = result.add_sheet('result', cell_overwrite_ok=True)
    cityRow=0
    start_date = datetime.datetime.now()
    mdate = "20" + datetime.date.today().strftime("%y-%m")
    cnt=1
    
    for key,val in weatherCityCode.items():
        print("%d--------------%s--%s-------------"%(cnt,key,val))
        old_data=getEveryMonthWeatherList(val, mdate, 0)
        future_data=get_future_15_days_weather(val)
        print("%d--------------%s--%s-------------\n"%(cnt,key,val))
        if old_data==None and future_data == None:
            continue
        write_data_to_excel(sheet, key, cityRow, old_data, future_data)
        cityRow = cityRow + 4
        result.save(r'./30days_weather.xls')
        cnt+=1
        time.sleep(0.5)
    
    result.save(r'./30days_weather.xls')
    end_date=datetime.datetime.now()
    print("\n",end_date - start_date,"(^_^)(^_^)(^_^)All city weather data get success!\n")

main()
