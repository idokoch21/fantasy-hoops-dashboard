import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from espn_api.basketball import League

# פונקציית עזר להוצאת הנתונים
def process_player_stats(player, year):
    stat_key = f"{year}_total"
    season_stats = player.stats.get(stat_key, {})
    total_stats = season_stats.get('total', {})
    games_played = season_stats.get('applied_avg', 1)
    if games_played == 0: games_played = 1
    
    get_val = lambda key: total_stats.get(key, 0)
    three_total = get_val('3PTM') or get_val('3PM') or get_val('3P')
    
    # יצירת ה-URL לתמונה של השחקן לפי ה-ID שלו
    img_url = f"https://a.espncdn.com/i/headshots/nba/players/full/{player.playerId}.png"
    
    return {
        "Img": img_url,
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
    }

@st.cache_data(ttl=600) # שומר את הנתונים ל-10 דקות (600 שניות)
def get_full_data():
    load_dotenv()
    league_id = int(os.getenv("LEAGUE_ID"))
    year = int(os.getenv("YEAR"))
    swid = os.getenv("SWID")
    espn_s2 = os.getenv("ESPN_S2")
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    
    # משיכת הקבוצה שלי
    my_team_name = "Ido's Impressive Team"
    my_team = next((team for team in league.teams if team.team_name == my_team_name), None)
    team_df = pd.DataFrame([process_player_stats(p, year) for p in my_team.roster]) if my_team else pd.DataFrame()
    
    # משיכת שוק חופשי
    fa_players = league.free_agents(size=100)
    fa_df = pd.DataFrame([process_player_stats(p, year) for p in fa_players])
    
    return team_df, fa_df