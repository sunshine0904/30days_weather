import json
import sys
import urllib.request
import urllib.error
import urllib.parse
import re
from bs4 import BeautifulSoup
import xlwt
import time
import datetime
from config import *
from old_days_weather import getEveryMonthWeatherList

#https://www.tianqiapi.com/user/login.php   register for account
#at least 5 account
account = [
        {"name":"jame7","appid":"67792497","appsecret":"8SQw4Uhj"},
]

class GetWeather:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        self.htmlResult = []
        self.loadList=[]
        self.cityList = []#格式为：列表里面的子列表都是一个省份的所有城市，子列表里所有元素都是字典，每个字典有两项
        self.cityDict={}
        self.result= xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.sheet = self.result.add_sheet('result', cell_overwrite_ok=True)
        self.cityRow=0
        self.totalGet=0
        with open("./CITY.txt", 'r',encoding='UTF-8') as load_f:
            loadList = json.load(load_f) #34个省份
            for i in range(0,4):
                self.cityList.append(loadList[i]['cityList'])
            for i in range(4, 34):
                for j in loadList[i]['cityList']:
                    self.cityList.append(j['districtList'])
            for i in self.cityList:
                for j in i:
                    if 'cityName' in j.keys():
                        self.cityDict.setdefault(j['cityName'], j['cityId'])   #直辖市
                    else:
                        self.cityDict.setdefault(j['districtName'], j['districtId'])  #省

    def __getWeatherInfo__(self, cityname):
        try:
            citycode = self.cityDict[cityname]
        except:
            print(cityname,"transto citycode error")
            return None
        #print(cityname, self.cityDict[cityname])
        account_id = 0
        PageUrl = "https://www.tianqiapi.com/api/?version=v2&cityid=" + citycode + "&appid=" + account[account_id]["appid"] + "&appsecret=" + account[account_id]["appsecret"] 
        request = urllib.request.Request(url=PageUrl, headers=self.headers)
        response = urllib.request.urlopen(request)
        #print("-------account name:", account[account_id]["name"], PageUrl, "response status:", response.status) 
        print(cityname, response.status, PageUrl)
        if response.status != 200:
            print("city id", id,"get data error")
        
        try:
            response_data = response.read().decode("utf-8")
            if len(response_data) < 75:
                print("response data decode error.",response_data,PageUrl)
                return None

            try:
                data_json = json.loads(response_data)
            except:
                print("json loads error.",cityname,PageUrl)
                return None
            
            try:
                mcity = data_json["city"]
            except:
                print("city error.",cityname)
                return None
            update_time = data_json["update_time"]
            weather_data = data_json["data"]
            return weather_data
        except:
            print("get future weather error",cityname,citycode,response.status,data_json,mcity,update_time,weather_data,PageUrl)
            data_json = 0
            mcity = 0
            update_time = 0
            weather_data = 0
            return None

    def __main__(self):
        start_date = datetime.datetime.now()
        date = "20" + datetime.date.today().strftime("%y-%m")
        cnt = 1
        for key,val in weatherCityCode.items():
            print(cnt, "---------", key)
            cnt = cnt + 1
            self.totalGet=self.totalGet + 1
            old_data = getEveryMonthWeatherList(val,date,0)
            future_data = self.__getWeatherInfo__(key)
           
            #error process
            if (old_data == None) or (future_data == None):
                print(key,"get data error")
                continue
	    
            
            self.sheet.write(self.cityRow, 0, key)  #写当前城市名
            column = 1
            for i in range(len(old_data)):
                self.sheet.write(self.cityRow, column, old_data[i][0])
                self.sheet.write(self.cityRow + 1, column, old_data[i][3])
                self.sheet.write(self.cityRow + 2, column, old_data[i][2])
                self.sheet.write(self.cityRow + 3, column, old_data[i][1])
                column = column + 1
            
            for i,val in enumerate(future_data):
                self.sheet.write(self.cityRow, column, val["date"])
                self.sheet.write(self.cityRow + 1, column, val["wea"])
                self.sheet.write(self.cityRow + 2, column, val["tem2"] + u'\u2103')
                self.sheet.write(self.cityRow + 3, column, val["tem1"] + u'\u2103')
                column = column + 1
            
            self.cityRow = self.cityRow + 4
            self.result.save(r'./30days_weather.xls')

            time.sleep(2)
        end_date = datetime.datetime.now()
        print(end_date - start_date)



xxx = GetWeather()
xxx.__main__()

