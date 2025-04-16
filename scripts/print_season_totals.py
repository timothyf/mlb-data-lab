import os
import pandas as pd
import re

from mlb_data_lab.config import LeagueTeams


def extract_team_abbrev(html_str):
    """
    Extract the team abbreviation from an HTML string, e.g.:
    '<a href="...">MIL</a>'  ->  'MIL'
    
    If html_str is not an HTML link, just returns the trimmed version.
    """
    if pd.isnull(html_str) or not isinstance(html_str, str):
        return html_str

    stripped = html_str.strip()

    # If the string does not look like an HTML link, return as-is.
    if not stripped.startswith("<a "):
        return stripped

    try:
        # Use a non-greedy regex to get text between ">" and "<"
        match = re.search(r">(.*?)<", stripped)
        if match:
            abbrev = match.group(1).strip()
            if abbrev:
                return abbrev
            else:
                return stripped
        else:
            # If we cannot find the pattern, return the trimmed string
            return stripped
    except Exception as e:
        # In case of unexpected errors, log and return the trimmed string.
        print(f"Error extracting team abbreviation from: {html_str} ({e})")
        return stripped

def set_league(df):
    """
    Set the league for each team based on the LeagueTeams mapping.
    """
    # Create a mapping of team abbreviations to leagues
    team_to_league = {team: league for league, teams in LeagueTeams.items.items() for team in teams}
    
    # Map the team abbreviations to their respective leagues
    df['League'] = df['Team'].map(team_to_league)
    
    # If the team abbreviation is not found, set it to None
    df['League'] = df['League'].where(df['League'].notnull(), None)


df = pd.read_csv("output/season_stats/stats_2024.csv")

df['Team'] = df['Team'].apply(extract_team_abbrev)
set_league(df)

if df['League'].isnull().any():
    missing_league_count = df['League'].isnull().sum()
    print(f"Number of teams with missing league: {missing_league_count}")
    missing_teams = df.loc[df['League'].isnull(), 'Team'].unique()
    print(f"Teams with missing league mapping: {missing_teams}")
    print("Warning: Some team abbreviations could not be mapped to a league.")

# --- (Optional) Inspect the first few rows ---
print(df[['Team', 'League']].head().to_string(index=False))
