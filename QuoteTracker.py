import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import time

#Gets scope for Google Sheets API Authentication
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# Pulls credentials from json file in directory
credentials = ServiceAccountCredentials.from_json_keyfile_name('StockTracer-16a2124cedb6.json', scope)

# Authorizes requests
gc = gspread.authorize(credentials)
# Sets var wks equal to the spreadsheet that we are using
wks = gc.open('test').sheet1

def stockInput():
    #This is the function used to input the stock 
    print("Please Input The Name of the Stock you are inputting: ")
    strStockName = input()

    print("Please Input The Stock Symbol of the Stock you are inputting")
    strStockSymbol = input()

    # This loop is used to check the input symbol aganist all other symbols to make sure the same symbol isnt entered twice
    counter = 0
    counterTotal = 0
    # Gets values of all cells in column 2
    valuesList = wks.col_values(2)

    # Goes through full list of values to check symbols
    for i in valuesList:
        counterTotal = counterTotal + 1
        if i == strStockSymbol.upper():
            print("This stock has already been entered!")
            break
        if i != strStockSymbol.upper():
            counter = counter + 1
    
    # If the input does not already exist within the spreadsheet, activate the next function
    if counter == counterTotal:
       newSpreadSheetStock(strStockName, strStockSymbol)     
            

    

def newSpreadSheetStock(strStockName, strStockSymbol): 
    # This is used to find the next row to slot in the stock information of Name and Stock Symbol
    columnValLen = len(wks.col_values(1))
    wks.update_cell(columnValLen + 1, 1 , strStockName)
    wks.update_cell(columnValLen + 1, 2 , strStockSymbol.upper())

    #Passes the stock symbol onto the next function
    stockUpdateRequest(strStockSymbol)
    


def stockUpdateRequest(strStockSymbol):
    #This grabs the information from the alpha vantage stock API in real time
    stockRequestDaily = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + strStockSymbol + '&outputsize=compact&apikey=5UXFHSVGPTYPKRE6')
    stockRequest = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + strStockSymbol + '&interval=15min&outputsize=full&apikey=5UXFHSVGPTYPKRE6')
    print('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + strStockSymbol + '&interval=15min&outputsize=full&apikey=5UXFHSVGPTYPKRE6')

    # Passes the stock symbol and the return from the Alpha Vantage API request to the next function
    stockSpreadSheetUpdate(strStockSymbol, stockRequest, stockRequestDaily)
    

def stockSpreadSheetUpdate(strStockSymbol, stockRequest, stockRequstDaily):
    # Decodes the JSON into a dict
    stockList = stockRequest.json()
    stockListDaily = stockRequstDaily.json()
    # Inside the Dict the last day that this stock was refreshed is held inside ["Meta Data"]["3. Last Refreshed"]
    # We grab this to make sure that we are getting the last time it was updated

    currentTimeKey = stockList["Meta Data"]["3. Last Refreshed"]
    lastDayDate = list(stockListDaily["Time Series (Daily)"].keys())[1]
    print(lastDayDate)

    # This will find the correct column and row for the stock and update the information passed into the function

    # Finds current row that the stock info is on
    currentCell = wks.find(strStockSymbol.upper())

    # This updates the appropriate cell with the closing information from that stocks listing for the current day
    wks.update_cell(currentCell.row, 3, stockList["Time Series (15min)"][currentTimeKey]["4. close"])
    wks.update_cell(currentCell.row, 5, stockListDaily["Time Series (Daily)"][lastDayDate]["4. close"])

def fullStockListUpdate():
    # This is called when the user wants to update the stock list
    # This will go through each row of stocks in the spreadsheet and will go through the functions stockUpdateRequest() and stockSpreadSheetUpdate()
    iStockRowCount = len(wks.col_values(1))

    apiCounter = 0
    for i in range(1,iStockRowCount):
        if (apiCounter >= 4):
            time.sleep(60)
            stockUpdateRequest(wks.cell(i+1,2).value)   
            apiCounter =  2
        elif (apiCounter <= 2):
            stockUpdateRequest(wks.cell(i+1,2).value)
            apiCounter = apiCounter + 2  
        
        
        pass

def __Main__():
    # This is the UI Console for the current script
    print("What would you like to do? Update | Add Stock")

    # Gets the user input to run through the if statement to determine what to do
    strUserAction = input().lower()
    if (strUserAction == "update"):
        fullStockListUpdate()
    elif (strUserAction == "add stock"):
        stockInput()
    else:
        print("Please enter one of the options above. Would you like to restart? yes | no")
        strUserRestartAction = input().lower()
        if (strUserRestartAction == "yes"):
            __Main__()
        else:
            print("Progam is ending... goodbye")





# This inits the main function in order to start the script
__Main__()


# Through the alpha vantage free api we are only allowed 5 calls per minute
# therefore we only want to update the daily once per day (or half day)
# and we want to do 4 calls per minute if including the daily call within the 15 minute call, you can only update 2 rows per minute
# Link to spreadsheet: https://docs.google.com/spreadsheets/d/1zehlqcXxsMimzoPFJw0nMnOAsmTDiRFQvk6kvGRolnA/edit#gid=0