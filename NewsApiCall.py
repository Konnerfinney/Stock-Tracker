#!/usr/bin/env python3
from credentials import apiKey
import requests
from requests.auth import HTTPBasicAuth



lenList = []
sourcesList = ['Bloomberg','CNBC','The-Wall-Street-Journal','Ars-Technica','Recode','Wired']

# Function to check source name aganist list of sources to not use
def isNotSource(testSource):
    for n in range(len(notSourceList)):
        if (testSource == notSourceList[n]):
            return True
    return False


def getNews(ticker_symbol: str, sources: list) -> str:
    # Forms the url in order to make the http request
    urlBase = 'https://newsapi.org/v2/everything?'
    keywordURL = 'q=' + ticker_symbol
    urlFull = urlBase + keywordURL + '&sources='

    # Adds sources into the url
    for sources in sources:
        urlFull = urlFull + sources + ','
    r = requests.get(urlFull, headers={'Authorization': apiKey})
    json_ret_dict = r.json()
    if json_ret_dict["status"] == "ok":
        return json_ret_dict["articles"][0]["url"]
    pass

# will be passed in tickerSymbol and return latest link to news article containing that company
def get_newest_news(tickerSymbol: str) -> str:
    return(getNews(tickerSymbol, sourcesList))
    





