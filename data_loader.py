import os
import pandas as pd
from dotenv import load_dotenv
from espn_api.basketball import League

# Load environment variables from the .env file
load_dotenv()

league_id = int(os.getenv("LEAGUE_ID"))
year = int(os.getenv("YEAR"))
swid = os.getenv("SWID")
espn_s2 = os.getenv("ESPN_S2")

print("Connecting to ESPN...")

# Connect to the league
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

print(f"Successfully connected to: {league.settings.name}!\n")

# --- Fetch Data ---
print("🏆 League Standings:")

# Print league standings
for index, team in enumerate(league.standings(), 1):
    print(f"{index}. {team.team_name} ({team.wins}W - {team.losses}L)")

# --- Fetch Your Team & Build Pandas DataFrame ---
print("\n🏀 Fetching Your Team Roster and creating a Pandas DataFrame...")

# Your exact team name as it appears in the standings
my_team_name = "Ido's Impressive Team"
my_team = None

# Find your team among all teams in the league
for team in league.teams:
    if team.team_name == my_team_name:
        my_team = team
        break

# If found, process the players into a table
if my_team:
    player_data = [] # Empty list to hold our player dictionaries
    
    for player in my_team.roster:
        # Create a dictionary for each player with relevant stats
        player_info = {
            "Name": player.name,
            "Position": player.position,
            "Pro Team": player.proTeam,
            "Injured": player.injured
        }
        player_data.append(player_info)
    
    # Convert the list of dictionaries into a Pandas DataFrame
    df = pd.DataFrame(player_data)
    
    print("\n📊 Your Team Data (Pandas DataFrame):")
    print(df.to_string()) # .to_string() prints the whole table nicely
    
else:
    print("Team not found, check the exact name!")