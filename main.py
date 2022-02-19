# SOFR rates and index
# RNS20220213
#
import pandas as pd
import urllib.request
from datetime import datetime as dt
from bs4 import BeautifulSoup
import math

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
  df.set_index('date',inplace=True,drop=True)
  return df
  # end fedQuery()


# get data from Fed 
endDt=dt(2022, 2, 18)
sofrONStartDt=dt(2018, 4, 2)
sofrIndexStartDt=dt(2020, 3, 2)

# two queries because data ranges are different
sofrdf=fedQuery('520','percentRate',sofrONStartDt,endDt) # SOFR ON
indexdf=fedQuery('525','index',sofrIndexStartDt,endDt) # SOFR Index
# combine into single series
alldf = pd.concat([sofrdf,indexdf],axis='columns',join='outer',ignore_index=False)
# add days between dates to series
dates=alldf.index
datelen=len(dates)
days=(dates[1:datelen]-dates[0:datelen-1]).days
days=days.append(pd.Index([math.nan])) # top off last day with null
alldf['days']=days # add days to df
alldf['dailyAccrual']=(alldf['percentRate']*alldf['days'])/36000+1.0

print(alldf)

dateStart = dt(2020,3,11)
dateEnd = dt(2021,3,11)
accrual_days = (dateEnd-dateStart).days
indexStart = alldf.loc[dateStart]['index']
indexEnd = alldf.loc[dateEnd]['index']

#mask=(alldf['date']>=dateStart) & (alldf['date']<dateEnd)
#print(rangedf)
accrualdf=alldf.loc[dateStart:dateEnd]
accrualdf.drop(accrualdf.tail(1).index,inplace=True) # drop last row

print('       accrual_days=',accrual_days) 

print('          accrualdf=',accrualdf)
accrual_compounded=accrualdf['dailyAccrual'].product()
rate_compounded = (accrual_compounded-1)*360/accrual_days
print('accrual(compounded)=',accrual_compounded)
print('   rate(compounded)=',rate_compounded)

print('          dateStart=',dateStart)
print('         indexStart=',indexStart)
print('            dateEnd=',dateEnd)
print('           indexEnd=',indexEnd)
accrual_index=indexEnd/indexStart
print('     accrual(index)=',accrual_index)
rate_index = (accrual_index-1)*360/accrual_days
print('        rate(index)=',rate_index)

print('    rate difference=',rate_compounded-rate_index)
print("END")
