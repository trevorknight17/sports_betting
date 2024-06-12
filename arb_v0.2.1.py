import requests
import tkinter as tk
from tkinter import messagebox
import webbrowser

def check_connection():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        if response.status_code == 200:
            return True
    except requests.Timeout:
        messagebox.showerror("Error","Request Timeout")
    except requests.ConnectionError:
        messagebox.showerror("Error","No Internet Connection")
        return False
    

def get_sports(api_key_entry):
    api_key = api_key_entry.get()
    if not api_key:
        messagebox.showerror("Error","Enter an API Key")
        return
    api_endpoint_sports = f'https://api.the-odds-api.com/v4/sports/?apiKey={api_key}'
    try:
        response_sports = requests.get(api_endpoint_sports)
        if response_sports.status_code == 200:
            data = response_sports.json()
            sports_only = [entry["key"] for entry in data]
            sports_listbox.delete(0, tk.END)
            for key in sports_only:
                sports_listbox.insert(tk.END, key)
        elif response_sports.status_code == 401:
            messagebox.showerror("Error","Unauthorized")
    except requests.ConnectionError:
        messagebox.showerror("Error","No Internet Connection")
        

def calculate_odds(api_key_entry, sport, result_text, max_unit_entry):
    if not sport:
        messagebox.showerror("Error","Select a sport")
        return
    max_unit = max_unit_entry.get()
    if not max_unit:
        messagebox.showerror("Error","Enter a Max Unit")
        return
    if not check_connection():
        return
    api_key = api_key_entry.get()
    max_unit = float(max_unit)

    api_endpoint = f'https://api.the-odds-api.com/v4/sports/{sport}/odds?regions=us&oddsFormat=american&apiKey={api_key}'

    try:
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()

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
                
            for game_index, (game_key, team_data) in enumerate(highest_prices_by_game.items(), start=0):
                result_text.insert(tk.END, "")
                result_text.insert(tk.END, f"Game Index: {game_index}\n")
                for team_name, data in team_data.items():
                    hp.append(data['highest_price'])
                if 2*game_index < len(hp) and 2*game_index + 1 < len(hp):    
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
                        ROI = profit / payout
                        ROId = "{:.2f}".format(ROI)
                        profit = "{:.2f}".format(profit)
                        if float(profit) > 0:
                            profits.append(f"${profit}({ROId}) in Game: {game_index}")    
                        staked = "{:.2f}".format(max_unit + unit)
                        ratio = "{:.2f}".format(max_unit / unit)
                        unit = "{:.2f}".format(unit)
                        payout = "{:.2f}".format(payout)
                        units = [unit, max_unit]
                        for index, (team_name, data) in enumerate(team_data.items()):
                            result_text.insert(tk.END, f"${units[index]} on {team_name} @ {data['highest_price']} on {data['highest_bookmaker']}")
                        result_text.insert(tk.END, f"Ratio: {ratio}")
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
                        ROI = profit / payout
                        ROId = "{:.2f}".format(ROI)
                        profit = "{:.2f}".format(profit)
                        if float(profit) > 0:
                            profits.append(f"${profit}({ROId}) in Game: {game_index}")  
                        staked = "{:.2f}".format(max_unit + unit)
                        ratio = "{:.2f}".format(max_unit / unit)
                        unit = "{:.2f}".format(unit)
                        payout = "{:.2f}".format(payout)
                        units = [max_unit, unit]
                        for index, (team_name, data) in enumerate(team_data.items()):
                            result_text.insert(tk.END, f"${units[index]} on {team_name} @ {data['highest_price']} on {data['highest_bookmaker']}")
                        result_text.insert(tk.END, f"Ratio: {ratio}")    
                else:
                    team_names = [team_name for team_name in team_data.keys()]
                    result_text.insert(tk.END, f"Game Index {game_index}: Not available for {' and '.join(team_names)}")

                result_text.insert(tk.END, f"Total Staked: ${staked}")
                result_text.insert(tk.END, f"Payout: ${payout}")
                result_text.insert(tk.END, f"Profit: ${profit}")
                if float(profit) > 0:
                    ROI = "{:.2f}".format(ROI)
                    result_text.insert(tk.END, f"ROI: {ROI}")

            result_text.insert(tk.END, "")
            result_text.insert(tk.END, f"Profitable MLs found: {profits}")
            result_text.insert(tk.END, "-----------------------------------------------------------------------------------")
        else:
            print('didnt work')

    except requests.exceptions.RequestException as e:
        result_label.config(text=f"Error: {e}")

def open_api_link(event):
    webbrowser.open("https://the-odds-api.com/")

# Create the main window
root = tk.Tk()
version_info = "(v0.2.1)"
root.title(f"Arb Calculator {version_info}")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set a minimum size for the window
root.minsize(700, 500)

# Configure row and column weights to make the grid scalable
for i in range(10):
    root.rowconfigure(i, weight=1)
    root.columnconfigure(i, weight=1)

# Create widgets
api_key_label = tk.Label(root, text="Access Key:")
api_key_entry = tk.Entry(root)
max_unit_entry_label = tk.Label(root, text="Max Unit:")
max_unit_entry = tk.Entry(root)
get_sports_button = tk.Button(root, text="Get Sports", command=lambda: get_sports(api_key_entry))

sports_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
sports_listbox_label = tk.Label(root, text="Sports:")
sportscrollbar = tk.Scrollbar(root, command=sports_listbox.yview)
sports_listbox.configure(yscrollcommand=sportscrollbar.set)
calculate_button = tk.Button(root, text="Calculate Odds", command=lambda: calculate_odds(api_key_entry, get_selected_sport(), result_listbox, max_unit_entry))

def get_selected_sport():
    selected_sport_index = sports_listbox.curselection()
    if selected_sport_index:
        return sports_listbox.get(selected_sport_index)
    else:
        return None

result_label = tk.Label(root, text="")
result_listbox = tk.Listbox(root, height=15, width=60)
result_listbox_label = tk.Label(root, text="Results:")
yscrollbar = tk.Scrollbar(root, command=result_listbox.yview)
result_listbox.configure(yscrollcommand=yscrollbar.set)
xscrollbar = tk.Scrollbar(root, command=result_listbox.xview, orient=tk.HORIZONTAL)
result_listbox.configure(xscrollcommand=xscrollbar.set)

access_label = tk.Label(root, text="Get Access Key", fg="blue", cursor="hand2")
access_label.bind("<Button-1>",open_api_link)

# Grid the widgets
api_key_label.grid(row=0, column=0, pady=5)
api_key_entry.grid(row=0, column=1, pady=5)
get_sports_button.grid(row=0, column=2, pady=5)
sports_listbox_label.grid(row=3, column=0, pady=5)
sports_listbox.grid(row=3, column=1, pady=5)
sportscrollbar.grid(row=3, column=2, pady=5, sticky=tk.N + tk.S)
max_unit_entry_label.grid(row=4, column=0, pady=5)
max_unit_entry.grid(row=4, column=1, pady=5)
calculate_button.grid(row=4, column=2, pady=5)
result_listbox_label.grid(row=5, column=0, pady=5, columnspan=2, sticky=tk.W)
result_listbox.grid(row=6, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W + tk.E + tk.N + tk.S)
yscrollbar.grid(row=6, column=2, sticky=tk.N + tk.S)
xscrollbar.grid(row=7, column=0, columnspan=2, pady=5, sticky=tk.W + tk.E)
access_label.grid(row=8, column=0, pady=5, columnspan=2, sticky=tk.W)

# Start the main loop
root.mainloop()