import os
import pandas as pd
from dotenv import load_dotenv
from espn_api.basketball import League

def get_league_connection():
    """Establishes connection to the ESPN League."""
    load_dotenv()
    league_id = int(os.getenv("LEAGUE_ID"))
    year = int(os.getenv("YEAR"))
    swid = os.getenv("SWID")
    espn_s2 = os.getenv("ESPN_S2")
    return League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

def process_player_stats(player, year):
    """Extracts all 9-cat stats for a player, handling API key variations."""
    stat_key = f"{year}_total"
    season_stats = player.stats.get(stat_key, {})
    total_stats = season_stats.get('total', {})
    games_played = season_stats.get('applied_avg', 1)
    if games_played == 0: games_played = 1
    
    get_val = lambda key: total_stats.get(key, 0)
    three_total = get_val('3PTM') or get_val('3PM') or get_val('3P')
    
    return {
        "Name": player.name,
        "Pos": player.position,
        "PTS": round(get_val('PTS') / games_played, 1),
        "REB": round(get_val('REB') / games_played, 1),
        "AST": round(get_val('AST') / games_played, 1),
        "STL": round(get_val('STL') / games_played, 1),
        "BLK": round(get_val('BLK') / games_played, 1),
        "TO": round(get_val('TO') / games_played, 1),
        "3PM": round(three_total / games_played, 1),
        "FG%": round(get_val('FG%') * 100, 1) if get_val('FG%') else 0,
        "FT%": round(get_val('FT%') * 100, 1) if get_val('FT%') else 0,
        "Injured": "Yes" if player.injured else "No"
    }

def get_my_team_data():
    league = get_league_connection()
    my_team_name = "Ido's Impressive Team"
    my_team = next((team for team in league.teams if team.team_name == my_team_name), None)
    if my_team:
        return pd.DataFrame([process_player_stats(p, league.year) for p in my_team.roster])
    return pd.DataFrame()

def get_free_agents(size=100):
    league = get_league_connection()
    fa_players = league.free_agents(size=size)
    return pd.DataFrame([process_player_stats(p, league.year) for p in fa_players])