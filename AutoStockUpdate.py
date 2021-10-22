#!/usr/bin/env python3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
from datetime import datetime
import pytz
import time
import NewsApiCall


#Gets scope for Google Sheets API Authentication
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# Pulls credentials from json file in directory
credentials = ServiceAccountCredentials.from_json_keyfile_name('StockTracer-16a2124cedb6.json', scope)

# Authorizes requests
gc = gspread.authorize(credentials)
# Sets var wks equal to the spreadsheet that we are using
wks = gc.open('Stock Tracking').sheet1

def stockUpdateRequest(strStockSymbol):
    #This grabs the information from the alpha vantage stock API in real time
    stockRequest = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + strStockSymbol + '&interval=15min&outputsize=full&apikey=5UXFHSVGPTYPKRE6')
    print('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + strStockSymbol + '&interval=15min&outputsize=full&apikey=5UXFHSVGPTYPKRE6')

    # Passes the stock symbol and the return from the Alpha Vantage API request to the next function
    stockSpreadSheetUpdate(strStockSymbol, stockRequest)

def stockUpdateDailyRequest(strStockSymbol):
    #This grabs the information from the alpha vantage stock API in real time
    stockRequestDaily = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + strStockSymbol + '&outputsize=compact&apikey=5UXFHSVGPTYPKRE6')
    # Passes the stock symbol and the return from the Alpha Vantage API request to the next function
    stockSpreadSheetDailyUpdate(strStockSymbol, stockRequestDaily)
    
def stockSpreadSheetUpdate(strStockSymbol, stockRequest):
    # Decodes the JSON into a dict
    stockList = stockRequest.json()
    # Inside the Dict the last day that this stock was refreshed is held inside ["Meta Data"]["3. Last Refreshed"]
    # We grab this to make sure that we are getting the last time it was updated

    currentTimeKey = stockList["Meta Data"]["3. Last Refreshed"]

    # This will find the correct column and row for the stock and update the information passed into the function

    # Finds current row that the stock info is on
    currentCell = wks.find(strStockSymbol.upper())

    # This updates the appropriate cell with the closing information from that stocks listing for the current day
    wks.update_cell(currentCell.row, 3, stockList["Time Series (15min)"][currentTimeKey]["4. close"])

def stockSpreadSheetDailyUpdate(strStockSymbol, stockUpdateRequestDaily):
     # Decodes the JSON into a dict
    stockListDaily = stockUpdateRequestDaily.json()
    # Inside the Dict the last day that this stock was refreshed is held inside ["Meta Data"]["3. Last Refreshed"]
    # We grab this to make sure that we are getting the last time it was updated
    lastDayDate = list(stockListDaily["Time Series (Daily)"].keys())[1]

    # This will find the correct column and row for the stock and update the information passed into the function

    # Finds current row that the stock info is on
    currentCell = wks.find(strStockSymbol.upper())

    # This updates the appropriate cell with the closing information from that stocks listing for the current day
    wks.update_cell(currentCell.row, 5, stockListDaily["Time Series (Daily)"][lastDayDate]["4. close"])
# Through the alpha vantage free api we are only allowed 5 calls per minute
# therefore we only want to update the daily once per day (or half day)
# and we want to do 4 calls per minute if including the daily call within the 15 minute call, you can only update 2 rows per minute
# Link to spreadsheet: https://docs.google.com/spreadsheets/d/1zehlqcXxsMimzoPFJw0nMnOAsmTDiRFQvk6kvGRolnA/edit#gid=0


# This is the section to automatically update the stock spreadsheet
# This is done in 2 sections
# The last day's closing price will be updated twice a day 6:00 AM and 2:00 PM PST
# The rest of the stocks are on 15 minute intervals so if there are more stocks than can be updated within the 15 minute interval (only 5 calls per minute) (only 75 calls per 15 minutes)
# Then it will update continously 


tz = pytz.timezone("US/Pacific")
currentTime = datetime.now(tz)
currentClockTime = (str(currentTime))[11:19]

stockRowCounter = 0
StockRowDailyCounter = 0

def mainLoop():

    global stockRowCounter

    print("Resuming Operations")
    # This is the call to update the last day's closing stock values
    if (currentClockTime[0:5] == "05:00" or currentClockTime[0:5] == "15:00"):
        updateLastDayClosingValue()

    # This will make the call to run 5 api calls to update the rows
    if (int(currentClockTime[0:2]) > 5 & int(currentClockTime[0:2]) < 14):
        # Get the amount of stocks in the spreadsheet by taking the all values in a column and subtracting the title value
        # This is used to make sure that we dont get an error by over indexing and submitting a stock symbol that doesn't exist
        #stckAmtCnt = len(wks.col_values(1)) -1

        # Sets the counter equal to 0
        '''if (stockRowCounter >= stckAmtCnt):
            stockRowCounter = 0'''

        
        

        # For loop to run the request 5 times
        for i in range(5):
            if (wks.cell(stockRowCounter + 2, 2).value == ""):
                stockRowCounter = 0
            print("Calling the API")
            ticker_symbol = wks.cell(stockRowCounter + 2, 2).value
            news_url = NewsApiCall.get_newest_news(ticker_symbol)
            wks.update_cell(stockRowCounter +2, 6, news_url)
            stockUpdateRequest(ticker_symbol)
            stockRowCounter = stockRowCounter + 1
    print("Sleeping for 60 seconds")
    time.sleep(60)
    __MainLoop__()

def updateLastDayClosingValue():

    global StockRowDailyCounter

    # Get the amount of stocks in the spreadsheet by taking the all values in a column and subtracting the title value
    # This is used to make sure that we dont get an error by over indexing and submitting a stock symbol that doesn't exist
    stckAmtCnt = len(wks.col_values(1)) -1
    # Sets the counter equal to 0
    if (StockRowDailyCounter >= stckAmtCnt):
        stockRowDailyDailyCounter = 0

    for i in range(2,6):
            stockUpdateDailyRequest(wks.cell(stockRowDailyDailyCounter + 2, 2).value)
            stockRowDailyDailyCounter = stockRowDailyDailyCounter + 1
    time.sleep(60)


if __name__ == "__main__":
    mainLoop()
