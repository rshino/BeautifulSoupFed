# SOFR rates and index
# RNS20220213
#
import pandas as pd
import urllib.request
from datetime import datetime as dt
from bs4 import BeautifulSoup

def date2ccyymmdd(dateObj):
  return dt.strftime(dateObj,'%Y-%m-%d')

def fedQuery(rateCode, rateName,startDate,endDate):
  url_str = 'https://markets.newyorkfed.org/read?startDt='+\
  date2ccyymmdd(startDate)+\
  '&endDt='+\
  date2ccyymmdd(endDate)+\
  '&productCode=50&eventCodes='+rateCode+'&sort=postDt:1&format=xml'
  request_url = urllib.request.urlopen(url_str)
  xmldata = request_url.read()
  #print(xmldata)
  soup = BeautifulSoup(xmldata,'xml')

  dates = soup.find_all('effectiveDate')
  rates = soup.find_all(rateName)

  data = []
  for i in range(0,len(dates)):
    rows = [dt.strptime(dates[i].get_text(),'%Y-%m-%d'),rates[i].get_text()]
    data.append(rows)
  df = pd.DataFrame(data,columns = ['date',rateName],dtype=float)
  df.set_index('date',inplace=True)
  return df


endDt=dt(2022, 2, 18)
sofrONStartDt=dt(2018, 4, 2)
sofrIndexStartDt=dt(2020, 3, 2)


sofrdf=fedQuery('520','percentRate',sofrONStartDt,endDt)
indexdf=fedQuery('525','index',sofrIndexStartDt,endDt)

alldf = pd.concat([sofrdf,indexdf],axis=1)
#print(alldf)

dateStart = dt(2020,3,11)
dateEnd = dt(2020,6,11)
accrual = dateEnd-dateStart
indexStart = alldf.loc[dateStart]['index']
indexEnd = alldf.loc[dateEnd]['index']

#mask=(alldf['date']>=dateStart) & (alldf['date']<dateEnd)
#print(rangedf)
print(alldf.loc[dateStart:dateEnd])
print(dateStart)
print(indexStart)
print(dateEnd)
print(indexEnd)
print(accrual)