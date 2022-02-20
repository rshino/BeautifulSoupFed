# SOFR rates and index
# RNS20220213
#
import pandas as pd
import urllib.request
from datetime import datetime as dt, timedelta,date
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import math

TODAY=date.today()
START_DATE_SOFR_ON=dt(2018, 4, 2)
START_DATE_SOFR_INDEX=dt(2020, 3, 2)
DAY_COUNT=360
# Fed data gleaned from XML links
# https://www.newyorkfed.org/markets/reference-rates/sofr
FEDMKT_URL='https://markets.newyorkfed.org/read'
SOFR_ON_REQCODE='520' 
SOFR_ON='percentRate'
SOFR_INDEX_REQCODE='525'
SOFR_INDEX='index'

def date2ccyymmdd(dateObj):
  return dt.strftime(dateObj,'%Y-%m-%d')

def fedQuery(rateCode, rateName,startDate,endDate):
  url_str = FEDMKT_URL+'?'+\
  '&startDt='+date2ccyymmdd(startDate)+\
  '&endDt='+date2ccyymmdd(endDate)+\
  '&productCode=50'+\
  '&eventCodes='+rateCode+'&sort=postDt:1&format=xml'
  request_url = urllib.request.urlopen(url_str)
  xmldata = request_url.read()
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

# dateShift(cal, base_date, match, shift)
#   given a base date (which may or may not be in cal) and 
#   cal        : dataframe busdays where index is datetime
#   base_date  : base date (e.g., coupon date)
#   match      : +1 find following date if no match (future)
#              : 0  exact date (returns None if not found)
#              : -1 find preceding date if no match (past)
#   shift      : number of busdays, shift>0 later, shift<0 earlier
def dateShift(cal, base_date, match, shift):
  if (match>0):
    locdir='bfill' # NEXT index value
  elif (match<0):
    locdir='ffill' # PREVIOUS index value
  else:
    locdir=None # exact
  unique_index=pd.Index(cal.index)
  maxloc=len(cal)
  try:
    loc=unique_index.get_loc(base_date,method=locdir)
    #loc=max(min(loc+shift,maxloc),0)
    #print(loc)
    return unique_index[loc+shift]
  except:
    return None



# get data from Fed 
# two queries because data ranges are different
sofrdf=fedQuery(SOFR_ON_REQCODE,SOFR_ON,START_DATE_SOFR_ON,TODAY) # SOFR ON
indexdf=fedQuery(SOFR_INDEX_REQCODE,SOFR_INDEX,START_DATE_SOFR_INDEX,TODAY) # SOFR Index
# combine into single series
alldf = pd.concat([sofrdf,indexdf],axis='columns',join='outer',ignore_index=False)
# add busday intervals between dates to series
dates=alldf.index
datelen=len(dates)
days=(dates[1:datelen]-dates[0:datelen-1]).days
days=days.append(pd.Index([math.nan])) # top off last day with null
alldf['days']=days # add days to df
# calculate dailyAccrual 
alldf['dailyAccrual']=(alldf[SOFR_ON]*alldf['days'])/(DAY_COUNT*100)+1.0

######################## setup complete #######################

d0 = dt(2020,3,11) 
d1 = d0+relativedelta(months=6)
shift=0
following=1
d0=dateShift(alldf,d0,following,shift)
d1=dateShift(alldf,d1,following,shift)
d1prevBD=dateShift(alldf,d1,following,-1)

accrual_days = (d1-d0).days
index0 = alldf.loc[d0][SOFR_INDEX]
index1 = alldf.loc[d1][SOFR_INDEX]

accrualdf=alldf.loc[d0:d1prevBD] # accrual stops 1 day before coupon date
#accrualdf.drop(accrualdf.tail(1).index,inplace=True) # drop last row

print('          accrualdf=\n',accrualdf)
print('       accrual_days=',accrual_days) 
accrual_compounded=accrualdf['dailyAccrual'].product()
rate_compounded = (accrual_compounded-1)*360/accrual_days
print('accrual(compounded)=',accrual_compounded)
print('   rate(compounded)=',rate_compounded)

print('          dateStart=',d0)
print('         indexStart=',index0)
print('            dateEnd=',d1)
print('           indexEnd=',index1)
accrual_index=index1/index0
print('     accrual(index)=',accrual_index)
rate_index = (accrual_index-1)*360/accrual_days
print('        rate(index)=',rate_index)

print('    rate difference=',rate_compounded-rate_index)
print("END")
