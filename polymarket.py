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
        "offset" : offset,
        "active" : "true",
        "closed" : "false"
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

def parse_market(market):
    #This will look into the polymarket markets
    markets = market.get("markets",[])
    #Check if the list is empty
    if not markets:
        return None
#Get the list of markets
    market_data = markets[0]
    if market_data.get("closed"):
        return None
#Get prices
    prices = market_data.get("outcomePrices",[])
    #checks if its a string runs prices to put it in a list
    if isinstance(prices, str):
        prices = json.loads(prices)
    if not prices:
        return None
    yes_price = float(prices[0])
    no_price = float(prices[1])

#Check liquidity
    liquidity = float(market_data.get("liquidityNum", 0))
    # if liquidity < 5000:
    #     return None

#Check Volume
    volume = float(market_data.get("volumeNum", 0))
    # if volume < 100:
    #     return None
    
    #Return dictonaary
    return {
    "id": market.get("id"),
    "category": "game",
    "event_title": market.get("title"),
    "yes_price": yes_price,
    "no_price": no_price,
    "liquidity": liquidity,
    "volume_24hr": volume,
    "platform": "polymarket",
    "url": f"https://polymarket.com/event/{market.get('slug')}",
}

def display_markets(markets):
    #First print the get_headers
    print(f"\n{'='*65}")
    print(f"POLYMARKET NBA - ALL LIVE MARKETS")
    print(f"Checked at : {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*65}\n")
    #Check if there are markets
    if not markets :
        print("No Live Markets Found")
        return
    #we will use the sort function same as kalshi code
    markets.sort(key = lambda x: x["liquidity"], reverse = True)
    #Then loop through markets
    for market in markets:
        print(market["event_title"])
        #Yes and no prices
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

#Same thing here prints the games
if __name__ == "__main__":
    print("Fetching ALL Polymarket NBA markets...\n")
    markets = get_all_nba_markets()
    print(f"\nTotal unique markets: {len(markets)}\n")
    display_markets(markets) 






