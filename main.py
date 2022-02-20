# SOFR rates and index
# RNS20220213
#
import pandas as pd
import urllib.request
from datetime import datetime as dt, timedelta
from bs4 import BeautifulSoup
import math

# dateInSample
#   given a base date and 
#   datedf     : dataframe where index is datetime
#   input_date : base date
#   shift      : +1 following date (future)
#              : 0  exact date (returns None if not found)
#              : -1 prior date (past)
def dateInSample(datedf, input_date, shift):
  x_date=input_date
  mindate=min(datedf.index)
  maxdate=max(datedf.index)
  retdate=None
  while(x_date>=mindate and x_date<=maxdate):
    try:
      datedf.loc[x_date]
      retdate= x_date
      break
    except Exception as e:
      if (shift==0):
        break
      x_date+=timedelta(shift)
  return retdate
  # dateInSample

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

######################## setup complete #######################

#print(alldf.loc[dt(2020,3,11)].iloc)
test_date = dt(2020,4,11)
unique_index=pd.Index(alldf.index)
loc=unique_index.get_loc(test_date,method='ffill')
print(loc,unique_index[loc])
loc=unique_index.get_loc(test_date,method='bfill')
print(loc,unique_index[loc])




adjusted_date = dateInSample(alldf,test_date,0)
print('test_date=',test_date,'adjusted_date=',adjusted_date)
test_date = dt(2020,4,11)
adjusted_date = dateInSample(alldf,test_date,1)
print('test_date=',test_date,'adjusted_date=',adjusted_date)
adjusted_date = dateInSample(alldf,test_date,-1)
print('test_date=',test_date,'adjusted_date=',adjusted_date)
'''
dateStart = dt(2020,3,11)
dateEnd = dt(2020,4,13)
accrual_days = (dateEnd-dateStart).days
indexStart = alldf.loc[dateStart]['index']
indexEnd = alldf.loc[dateEnd]['index']

accrualdf=alldf.loc[dateStart:dateEnd]
accrualdf.drop(accrualdf.tail(1).index,inplace=True) # drop last row

print('          accrualdf=',accrualdf)
print('       accrual_days=',accrual_days) 
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
'''