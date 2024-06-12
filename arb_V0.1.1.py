import requests
import json

# API key available @https://the-odds-api.com/ 

apiKey = input('Enter access key:')

api_endpoint_sports = f'https://api.the-odds-api.com/v4/sports/?apiKey={apiKey}'

try:
    response_sports = requests.get(api_endpoint_sports)
    if response_sports.status_code == 200:
        sports = response_sports.json()
        sports_only = [entry["key"] for entry in sports]
        for key in sports_only:
            print(key)
        sport = input('Enter one sport: ')
    elif response_sports.status_code == 401:
        print('Unauthorized')

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

# Replace 'your-api-endpoint' with the actual API endpoint URL
api_endpoint = f'https://api.the-odds-api.com/v4/sports/{sport}/odds?regions=us&oddsFormat=american&apiKey={apiKey}'

try:
    # Make the API request
    response = requests.get(api_endpoint)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and work with the API response data
        data = response.json()  # Assumes the response is in JSON format

        # Initialize a dictionary to store the highest bookmaker, price, and opponent for each team, organized by game
        highest_prices_by_game = {}

        # Loop through the data to find the book with the highest price for each team in "h2h" market, organized by game
        for event in data:
            game_key = event["id"]
            highest_prices_by_game[game_key] = {}

            for bookmaker in event["bookmakers"]:
                h2h_market = next((market for market in bookmaker["markets"] if market["key"] == "h2h"), None)
                if h2h_market:
                    for outcome in h2h_market["outcomes"]:
                        team_name = outcome["name"]
                        price = outcome["price"]

                        if (
                            team_name not in highest_prices_by_game[game_key]
                            or price > highest_prices_by_game[game_key][team_name]["highest_price"]
                        ):
                            highest_prices_by_game[game_key][team_name] = {
                                "highest_bookmaker": bookmaker["title"],
                                "highest_price": price
                            }

        # Print the highest prices organized by game
        hp = []
        profits = []
        max_unit = 100
        for game_index, (game_key, team_data) in enumerate(highest_prices_by_game.items(), start=0):
            print(f"Game Index: {game_index}")
            for team_name, data in team_data.items():
                hp.append(data['highest_price'])
                print(f"  Team: {team_name}")
                print(f"    Bookmaker with the highest price: {data['highest_bookmaker']}")
                print(f"    Highest price: {data['highest_price']}")

            if (hp[2*game_index]) > (hp[2*game_index + 1]):
                if hp[2*game_index + 1] > 0:
                    payout = max_unit + (hp[2*game_index + 1] / 100) * max_unit
                else:
                    payout = max_unit + (100 / -hp[2*game_index + 1]) * max_unit
                if hp[2*game_index] > 0:
                    unit = payout / (1 + (hp[2*game_index] / 100))
                else:
                    unit = payout / (1 - (100 / hp[2*game_index]))
                profit = payout - (max_unit + unit)
                profit = "{:.2f}".format(profit)
                if float(profit) > 0:
                    profits.append(f"Profit of ${profit} in Game: {game_index}")    
                staked = "{:.2f}".format(max_unit + unit)
                unit = "{:.2f}".format(unit)
                print(f"${max_unit} on {hp[2*game_index + 1]}")
                print(f"${unit} on {hp[2*game_index]}")
            else:
                if hp[2*game_index] > 0:
                    payout = max_unit + (hp[2*game_index] / 100) * max_unit
                else:
                    payout = max_unit + (100 / -hp[2*game_index]) * max_unit
                if hp[2*game_index + 1] > 0:
                    unit = payout / (1 + (hp[2*game_index + 1] / 100))
                else:
                    unit = payout / (1 - (100 / hp[2*game_index + 1]))
                profit = payout - (max_unit + unit)
                profit = "{:.2f}".format(profit)
                if float(profit) > 0:
                    profits.append(f"Profit of ${profit} in Game Index: {game_index}") 
                staked = "{:.2f}".format(max_unit + unit)
                unit = "{:.2f}".format(unit)
                print(f"${max_unit} on {hp[2*game_index]}")
                print(f"${unit} on {hp[2*game_index + 1]}")       

            payout = "{:.2f}".format(payout)
            print(f"Total Staked: ${staked}")
            print(f"Payout: ${payout}")
            print(f"Profit: ${profit}")

        print(f"Profitable MLs found: {profits}")

    else:
        print('Sport not available')

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

input("Press Enter to exit.")