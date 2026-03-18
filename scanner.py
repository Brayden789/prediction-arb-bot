from teams import TEAM_NAMES
from kalshi import get_all_nba_markets as get_kalshi_markets
from polymarket import get_all_nba_markets as get_polymarket_markets
from dotenv import load_dotenv
import os
load_dotenv()

#Function gets the name of each team from the kalshi market then throws it
#Into the teams lookup then gets back the correct name
def extract_teams(event_title):
    market_title = event_title
    teams_name = market_title.split(" at ")
    team_one = teams_name[0].strip().lower()
    team_two = teams_name[1].replace(" Winner?", "").strip().lower()

    nickname_one = TEAM_NAMES.get(team_one)
    nickname_two = TEAM_NAMES.get(team_two)

    return nickname_one, nickname_two
#This fucntion will use the names gotten from extract teams
#Then check which polymarket markets have those names
#Then will match those markets
def find_match(polymarketmarkets, kalshi_market):
    nickname_one, nickname_two = extract_teams(kalshi_market["event_title"])
    for markets in polymarketmarkets:
        poly_title = markets["event_title"].lower()
        if nickname_one in poly_title and nickname_two in poly_title:
            return markets
    return None

def check_arbitrage(polymarket_market, kalshi_market):
    kalshi_yes = kalshi_market.get("yes_price")
    kalshi_no = kalshi_market.get("no_price")
    polymarket_no = polymarket_market.get("no_price")
    polymarket_yes = polymarket_market.get("yes_price")

    combo_one = kalshi_yes + polymarket_no
    combo_two = kalshi_no + polymarket_yes

    return combo_one, combo_two


def main():
    KALSHI_API_KEY = os.getenv("KALSHI_API_KEY")

    kalshimarkets = get_kalshi_markets(KALSHI_API_KEY)
    polymarketmarkets = get_polymarket_markets()

    for market in kalshimarkets:
        match = find_match(polymarketmarkets, market)
        if match:
            combo_one, combo_two = check_arbitrage(match, market)
            print(f"{market['event_title']}")
            print(f"  Kalshi YES + Poly NO: ${combo_one:.3f}")
            print(f"  Kalshi NO + Poly YES: ${combo_two:.3f}")
            print()

if __name__ == "__main__" :
    main()