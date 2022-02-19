# SOFR rates and index
# RNS20220213
#
import pandas as pd
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup

def fedQuery(rateCode, rateName,startDate,endDate):
  url_str = 'https://markets.newyorkfed.org/read?startDt='+startDate+'&endDt='+endDate+'&productCode=50&eventCodes='+rateCode+'&sort=postDt:1&format=xml'
  request_url = urllib.request.urlopen(url_str)
  xmldata = request_url.read()
  #print(xmldata)
  soup = BeautifulSoup(xmldata,'xml')

  dates = soup.find_all('effectiveDate')
  rates = soup.find_all(rateName)

  data = []
  for i in range(0,len(dates)):
    rows = [datetime.strptime(dates[i].get_text(),'%Y-%m-%d'),rates[i].get_text()]
    data.append(rows)
  df = pd.DataFrame(data,columns = ['date',rateName],dtype=float)
  df.set_index('date',inplace=True)
  return df



#startDt='2020-03-02'
sofrONStartDt='2018-04-02'
sofrIndexStartDt='2020-02-15'
endDt='2022-02-15'
sofrdf=fedQuery('520','percentRate',sofrONStartDt,endDt)
indexdf=fedQuery('525','index',sofrIndexStartDt,endDt)

alldf = pd.concat([sofrdf,indexdf],axis=1)
print(alldf)

datekey = datetime.strptime('2022-02-14','%Y-%m-%d')
row = alldf.loc[datekey]
print(row)


"""
startDt=sofrONStartDt
eventCodes='520'
url_str = 'https://markets.newyorkfed.org/read?startDt='+startDt+'&endDt='+endDt+'&productCode=50&eventCodes='+eventCodes+'&sort=postDt:1&format=xml'

request_url = urllib.request.urlopen(url_str)
xmldata = request_url.read()
#print(xmldata)
soup = BeautifulSoup(xmldata,'xml')

dates = soup.find_all('effectiveDate')
rates = soup.find_all('percentRate')
#print(dates)
data = []
for i in range(0,len(dates)):
   rows = [dates[i].get_text(),rates[i].get_text()]
   data.append(rows)
sofrdf = pd.DataFrame(data,columns = ['date','rate'],dtype=float)
sofrdf.set_index('date',inplace=True)

#startDt='2020-03-02'
startDt=sofrIndexStartDt
endDt='2022-02-15'
eventCodes='525'
url_str = 'https://markets.newyorkfed.org/read?startDt='+startDt+'&endDt='+endDt+'&eventCodes='+eventCodes+'&productCode=50&sort=postDt:1,eventCode:1&format=xml'

request_url = urllib.request.urlopen(url_str)
xmldata = request_url.read()
soup = BeautifulSoup(xmldata,'xml')

dates = soup.find_all('effectiveDate')
index = soup.find_all('index')
#print(dates)
data = []
for i in range(0,len(dates)):
   rows = [dates[i].get_text(),index[i].get_text()]
   data.append(rows)
indexdf = pd.DataFrame(data,columns = ['date','index'],dtype=float)
indexdf.set_index('date',inplace=True)
print(indexdf)
"""


