import statsapi

player_id = 682985  # Replace with actual player ID
year = 2024       # Replace with actual year

# Fetch player stats with advanced stat group
# player_stats = statsapi.get('people', {
#     'personIds': player_id, 
#     'season': year, 
#     'hydrate': 'stats(group=[hitting],type=season,season={year},statType=batting)'
# })

stats = statsapi.get('people', {'personIds': player_id, 'season': year, 
                                'hydrate': f'stats(group=[hitting],type=season,season={year},statType=advanced)'}
                    )['people'][0]

print (f"stats = {stats}")


from pybaseball import statcast_batter
from pybaseball import playerid_lookup

# find David Ortiz's player id (mlbam_key)
playerid_lookup('ortiz','david')

# get all available data
data = statcast_batter('2008-04-01', '2017-07-15', player_id = 120074)
print (f"data = {data}")

# get data for August 16th, 2014
data = statcast_batter('2014-08-16', player_id = 120074)
