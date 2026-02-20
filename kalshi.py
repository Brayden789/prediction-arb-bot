import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

#BASE URL
BASE_URL = "https://demo-api.kalshi.co/trade-api/v2"

"""
Pulls the active data from NBA Markets on kalshi using their demo API
 1. Daily game moneylines  
    2. Championship futures
    3. Finals markets
    4. MVP markets 
"""


def get_headers(api_key):
    return {"Authorization": f"ApiKey {api_key}", "Content-Type": "application/json"}

#This function gets the nba market data from the api key

def get_all_nba_markets(api_key):
    all_markets = []
    cursor = None
    limit = 100
    max_pages = 10
    #next we will create a loop
    #we will look through the max ammount of max_pages
    for page in range(max_pages):
        #This line we go into kalshi api then ask for a page of Markets
        #it will return 2 things the page and the cursor to the next page
        market_page,cursor = fetch_market_page(api_key,cursor,limit)
    #Each time we will loop through and return a list of markets and a new cursor

    #If the page is empty we will stop looking
        if not market_page:
            break
    #If not empty we will add whatever comes back to all markets
        else:
            all_markets.extend(market_page)
    #If there is no curssor(WE means we stop looping) (WE hit the last page)
        if not cursor:
            break
    return all_markets

#This is the method where we get the data for the bot
def fetch_market_page(api_key,cursor,limit):
    #first we will build the url we will want hings like, only show open markets
    #give me 100 at a time, then all those will be stored in a dictionatry which we will call on later
    url = f"{BASE_URL}/markets"

    params = {
        "status" : "open",
        "limit" : limit,
        "series_ticker" : "KXNBAGAME"
    }
    if cursor :
        params["cursor"] = cursor
    #error handling (try/except)
    #we will try something then if it doesnt work it will jump to the accept bloc
    try:
        #we will then use request.get to get to the kalshi servers we will give it the parameters
        #this will store kalshis response with all the data we asked for
        response = requests.get(url,params=params)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return [], None
    #once we get a response well pull out the data we need
    #get new variables and return the new curor and the
    #market data

    events = response.json()
    newcur = events.get("cursor",None)
    markets_raw = events.get("markets",[])

    seen_event_tickers = set()

    parsed = []
    for market in markets_raw:
        event_ticker = market.get("event_ticker")
        m = parse_market(market)
        if m:
            #This checks if the event is already there because kalshi is weird abt it
            if event_ticker not in seen_event_tickers:
                parsed.append(m)
                seen_event_tickers.add(event_ticker)
    return parsed, newcur

def parse_market(market):
    # print(market)
    # print("---")

    #This function will take a market and check if it follows our conditions
    marketstatus = market.get("status")
    #Check for it being an active market
    if marketstatus != "active":
        return None

    #check for liquidity
    liquidity = float(market.get("liquidity"))
    # if liquidity < 0:
    #     return None

    #check for volume
    volume = float(market.get("volume_24h"))
    # if volume < 0:
    #     return None
    #convert prices like 84 to 0.84
    yesWhole_price = market.get("yes_ask")
    noWhole_price = market.get("no_ask")

    if yesWhole_price is None or noWhole_price is None:
        return None

    yes_price = yesWhole_price /100
    no_price = noWhole_price /100
    # if it passed return the data
    return {
    "id" : market.get("ticker"),
    "category" : "game",
    "event_title" : market.get("title"),
    "yes_price" : yes_price,
    "no_price" : no_price,
    "liquidity" : liquidity,
    "volume_24hr" : volume,
    "platform" : "kalshi",
    "url": f"https://kalshi.com/markets/{market.get('ticker')}",
    }

def display_markets(markets):
    #First print the get_headers
    print(f"\n{'='*65}")
    print(f"KALSHI NBA - ALL LIVE MARKETS")
    print(f"Checked at : {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*65}\n")

    #THen check if there are open Kalshi Markets
    if not markets :
        print("No Live Markets Found")
        return

    #Then use the sort function to sort the markets by the most liquid
    #Means for each market in x look at its liquidity Then reverse= true means
    #print the higest first
    markets.sort(key = lambda x: x["liquidity"], reverse = True)
    #Then loop througb each market and print:
    for market in markets:
    #The title event
        print(market["event_title"])
    #Yes and NO price
        yes_price = market["yes_price"]
        no_price = market["no_price"]
        combined = round(yes_price + no_price, 4)
        gap = round((1-combined)*100,2)
        print(f"YES:${yes_price:.3f}")
        print(f"NO:${no_price:.3f}")

    #Combined price and the gap if its over 2%
        if gap >2:
                print("GAP Found")

    #Liquidity and volume
        print("Liquidity: ", market["liquidity"])
        print("Volume: ", market["volume_24hr"])


#Final part of the script that prints the games using Kalshis API key    
if __name__ == "__main__":

    API_KEY = os.getenv("KALSHI_API_KEY")
    print("Fetching ALL Kalshi NBA markets...\n")
    markets = get_all_nba_markets(API_KEY)
    print(f"\nTotal unique markets: {len(markets)}\n")
    display_markets(markets)




