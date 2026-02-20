import requests
import json
from datetime import datetime


#BASE URL
BASE_URL = "https://gamma-api.polymarket.com"

#This fucntion will loop through the kalshi markets and get the nba markets
def get_all_nba_markets():
    all_markets = []
    offset = 0
    limit =100
    max_pages = 10

    for pages in range(max_pages):
        #We will call the polymarket api and we will get the page of markets back
        market_page = fetch_market_page(offset,limit)
        #check if page is empty
        if not market_page:
            break
        #If not empty we will add what comes to market page
        else:
            all_markets.extend(market_page)
        #if there is no offset we stop beacsue we hit the last page
        if len(market_page) < limit:
            break
        offset = offset + limit
    #Return what we got
    return all_markets

#Same thing as kalshi well get the data for the bot here
def fetch_market_page(offset, limit):
    #We will build the URL, then get a dictonaary of params just like kalshi
    #we use evnts instead of markets like in kalshi
    url = f"{BASE_URL}/events"
    
    params = {
        "limit" : limit,
        "tag_slug" : "nba",
        "offset" : offset
    }

    #we will then use try and except block to store the response for polymarket
    try :
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

    #once we pull out that data we need we will then return the market data
    markets_raw = response.json()

    #then we create a loop that calls parse market on each raw market we got
    #we create a new lsit that after each makret is parsed we will then add those 
    #markets to the parsed list

    parsed = []
    for markets in markets_raw:
        p = parse_market(markets)
        if p:
            parsed.append(p)
    return parsed








