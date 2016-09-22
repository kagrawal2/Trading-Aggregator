from yahoo_finance import Share
from bs4 import BeautifulSoup
import requests
import csv
import re
import numpy as np
import os
import pandas as pd
import datetime
from sectorIndustry import sectorData

finalData = {}
rows = []

"""This system revolves around market releases and information by quarter. By Kireet Agrawal
This creates a dataset with verification, in the future, more sources will be added such as Twitter, and News parsing.
"""
#Set up settings for desired data. 
forwardDays = 5
backwardDays = 5
sectorDataDict = sectorData

headers = ['pre-post', 'co', 'report date','end of quarter', 'forecastEPS','numEst','last Report date', 'actualEPS','percent Surprise']
#headers.append('time')
headers.append('ticker sym')
headers.append('marketCap')
headers.append('sector')
headers.append('industry')
lst = []
i = forwardDays
while i >= 0:
    lst.append('t' + str(i))
    lst.append('o' + str(i))
    lst.append('h' + str(i))
    lst.append('l' + str(i))
    lst.append('c' + str(i))
    i -= 1
j = 1
while j <= backwardDays:
    lst.append('t-' + str(j))
    lst.append('o-' + str(j))
    lst.append('h-' + str(j))
    lst.append('l-' + str(j))
    lst.append('c-' + str(j))
    j += 1

for x in lst:
    headers.append(x)

rows.append(headers)
finalData['titles'] = headers



def buildDate(date):
    """
    >>> buildDate(2016-Apr-18)
    Apr 18, 2016"""
    parts = date.split("-")
    yDate = parts[1] + " " + parts[2] + ', ' + parts[0]
    return yDate

def rebuildDate(date):
    """
    >>> rebuildDate(Apr 18, 2016)
    2016-Apr-18
    """
    parts = date.split(" ")
    parts[1] = parts[1][:-1]
    eDate = parts[2] + '-' + parts[0] + '-' + parts[1]
    return eDate

monthToInt = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06', 
              'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

def yDate(date):
    """
    >>> yDate(2016-Apr-18)
    '2016-04-18'
    """
    parts = date.split("-")
    return parts[0] + '-' + monthToInt[parts[1]] + '-' + parts[2]

def dateRange(t0):
    return [datetime.datetime.strftime(n,'%Y-%m-%d') for 
     n in pd.bdate_range(end=t0, periods= forwardDays + 1).date] + [datetime.datetime.strftime(n,'%Y-%m-%d') for 
     n in pd.bdate_range(start=t0, periods= backwardDays + 1).date 
     if datetime.datetime.strftime(n,'%Y-%m-%d') <= datetime.datetime.now().strftime('%Y-%m-%d')][1:]

def getTicker(string):
    #From the earnings calendar, obtain the 
    #ticker name from second array entry as the string
    tickList = re.findall(r"\(([A-Za-z0-9_]+)\)", string)
    if len(tickList) != 0:
        return tickList.pop()
    else:
        return ''

def checkDividend(s): 
    #In yahoo finance remove any divendend 
    #rows that are unwanted.
    a = ['divide', 'dividend', 'Dividend']
    string = s.lower()
    return any(x in string for x in a)
    
def getMarketCap(s):
    parts = s.split(" ")
    return parts.pop()

def getMarketTime(s):
    if 'pre' in s:
        return 'pre'
    elif 'Pre' in s:
        return 'pre'
    elif 'after' in s:
        return 'post'
    elif 'After' in s:
        return 'post'
    else:
        return ''

def cleanData(string):
    string = string.replace("$", "")
    string = string.replace('Met', '0')
    string = string.replace('n/a', 'np.nan')
    string = string.replace('N/A', 'np.nan')
    try:
        return np.float(string)
    except:
        if string == 'np.nan':
            return eval(string)
        return string




# def parseBusinessWire(date):
#     url = "http://mmm.wallstreethorizon.com/cal_gen/cal_gen.asp?opt=/BIZWIRE&date=" + #4/28/2016 
#     response = requests.get(url)
#     html = response.content
#     yDate = buildDate(date)
    
#     soup = BeautifulSoup(html)

#Obtain actualEPS and time from businessWire for only current days to build database
                # try:
                    # parseBusinessWire(date)
                    # data[7] = actualEPS
                # except:
                    # print(business wire EPS not found)
                # try:
                    # parseBusinessWire(date)
                    # data[9] = actualTime
                # except:
                    # print(business wire Time not found)


# def parseNasdaqEarningsReport():
    #Obtain actualEPS and time from NASDAQ EarningsReport for all
        # try:
            # parseNASDAQ(date) 
            # -> forecastedEPS, actualEPD, && add yahoo-finance query
            # for each date from the last quarter
            # stock.get_historical(dateRange(date)[0], dateRange(date)[-1])
        # except:
            #  past Data not found




def parseForDay(date):
    """
    parseForDay("2016-Apr-29")
    """
    url = "http://www.nasdaq.com/earnings/earnings-calendar.aspx?date=" + date
    response = requests.get(url)
    html = response.content
    yDate = buildDate(date)
    
    soup = BeautifulSoup(html)
    table = soup.find(attrs={"class":"genTable"})
    dailyRow = []
    
    for row in table.find_all('tr'):
        data = []
        for td in row.find_all('td'):
            if td.find('img') != None:
                data.append(getMarketTime(str(td.find('img'))))
            else:
                data.append(cleanData(td.get_text().strip()))

        if len(data) == 9:
            # print(data[0])
            #data.append(getMarketTime(data[0]))
            try:
                data.append(getTicker(data[1]))
                # print(getTicker(data[1]))
                # if getTicker(data[1]) not in stockSplits:
                data.append(cleanData(getMarketCap(data[1])))

                try:
                    data.append(cleanData(sectorDataDict[getTicker(data[1])][0]))
                except:
                    data.append(np.nan)
                    print('Not found in Sector Data: ' + getTicker(data[1]))
                try:
                    data.append(cleanData(sectorDataDict[getTicker(data[1])][1]))
                except:
                    data.append(np.nan)
                    print('Not found in Industry Data: ' + getTicker(data[1]))

                try:
                    stock = Share(getTicker(data[1]))
                    # print(stock.get_historical(dateRange(date)[0], dateRange(date)[-1]))
                    stockData = stock.get_historical(dateRange(date)[0], dateRange(date)[-1])
                    for x in stockData:
                        data.append(cleanData(x['Date']))
                        data.append(cleanData(x['Open']))
                        data.append(cleanData(x['Close']))
                        data.append(cleanData(x['High']))
                        data.append(cleanData(x['Low']))
                        # data.append(x['Volume'])
                    dailyRow.append(data)
                    rows.append(data)
                except:
                    print('Yahoo-Finance does not have: ' + getTicker(data[1]))

            except:
                print('Error for stock: ' + getTicker(data[1]))

    return dailyRow
# parseForDay("2016-Apr-29")

def parseFileRange(startDate, number):
    """parseForDay("2016-Apr-18", 10)"""

    fileName = startDate + '.csv'
    daysToParse = [datetime.datetime.strftime(n,'%Y-%m-%d') for 
     n in pd.bdate_range(end=startDate, periods=number).date][::-1]

    for day in daysToParse:
        # fileName = str(currentDate) + '.csv'
        # rows = parseForDay(currentDate)
        print(day)
        parseForDay(day)

        fP = os.path.join('dates/', fileName)
        with open(fP, 'w', newline='') as csvfile: #change w to a
            a = csv.writer(csvfile, delimiter=',')
            a.writerows(rows)

def parseRange(startDate, number):
    """parseForDay("2016-Apr-18", 10)"""
    daysToParse = [datetime.datetime.strftime(n,'%Y-%m-%d') for 
     n in pd.bdate_range(end=startDate, periods=number).date][::-1]

    for day in daysToParse:
        print(day)
        finalData[day] = parseForDay(day)

    return rows


today = datetime.datetime.now().strftime('%Y-%m-%d')
parseFileRange('2016-Apr-22', 40)



