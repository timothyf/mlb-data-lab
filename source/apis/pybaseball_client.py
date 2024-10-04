import pybaseball as pyb



class PybaseballClient: 

    # Split types returned:
        # ['Career Totals', 'Last 7 days', 'Last 14 days', 'Last 28 days', 'Last 365 days', 'vs RHP', 'vs LHP', 
        #  'vs RHP as LHB', 'vs LHP as LHB', 'vs RH Starter', 'vs LH Starter', 'Home', 'Away', '1st Half', '2nd Half', 
        #  'April/March', 'May', 'June', 'July', 'August', 'Sept/Oct', 'in Wins', 'in Losses', 'as Starter', 'as Sub', 
        #  'as LF', 'as CF', 'as RF', 'as DH', 'as PH', '1st Batter G', 'Leadoff Inn.', 'Batting 1st', 'Batting 2nd', 
        #  'Batting 3rd', 'Batting 4th', 'Batting 5th', 'Batting 6th', 'Batting 9th', 'Swung at 1st Pitch', 'Took 1st Pitch', 
        #  'First Pitch', '1-0 Count', '2-0 Count', '3-0 Count', '0-1 Count', '1-1 Count', '2-1 Count', '3-1 Count', 
        #  '0-2 Count', '1-2 Count', '2-2 Count', 'Full Count', 'After 1-0', 'After 2-0', 'After 3-0', 'After 0-1', 
        #  'After 1-1', 'After 2-1', 'After 3-1', 'After 0-2', 'After 1-2', 'After 2-2', 'Zero Balls', 'Zero Strikes', 
        #  'Three Balls', 'Two Strikes', 'Batter Ahead', 'Even Count', 'Pitcher Ahead', '0 outs', '1 out', '2 outs', 
        #  'RISP', '---', 'Men On', '1--', '-2-', '--3', '12-', '1-3', '-23', '123', 'on 1st, <2 out', 'on 3rd, <2 out', 
        #  'on 3rd, 2 out', '0 out, ---', '0 out, 1--', '0 out, -2-', '0 out, --3', '0 out, 12-', '0 out, 1-3', '0 out, -23', 
        #  '0 out, 123', '1 out, ---', '1 out, 1--', '1 out, -2-', '1 out, --3', '1 out, 12-', '1 out, 1-3', '1 out, -23', 
        #  '1 out, 123', '2 out, ---', '2 out, 1--', '2 out, -2-', '2 out, --3', '2 out, 12-', '2 out, 1-3', '2 out, -23', 
        #  '2 out, 123', '2 outs, RISP', 'Late & Close', 'Tie Game', 'Within 1 R', 'Within 2 R', 'Within 3 R', 'Within 4 R', 
        #  'Margin > 4 R', 'Ahead', 'Behind', 'High Lvrge', 'Medium Lvrge', 'Low Lvrge', 'vs. SP', 'vs. RP', 'vs. SP, 1st', 
        #  'vs. SP, 2nd', 'vs. SP, 3rd', 'vs. SP, 4th+', 'vs. RP, 1st', 'vs. RP, 2nd', 'vs. Power', 'vs. avg.P/F', 
        #  'vs. Finesse', 'vs. Fly Ball', 'vs. avg.F/G', 'vs. GrndBall', 'To Infield', 'To Outfield', 'Ball In Play', 
        #  'Not in Play', 'Fair Terr', 'Foul Terr', 'Pulled-LHB', 'Up Mdle-LHB', 'Opp Fld-LHB', 'Ground Balls', 'Fly Balls', 
        #  'Line Drives', 'Inter-League', 'Los Angeles Angels', 'Arizona Diamondbacks', 'Atlanta Braves', 'Baltimore Orioles', 
        #  'Boston Red Sox', 'Chicago Cubs', 'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Guardians', 'Colorado Rockies', 
        #  'Miami Marlins', 'Houston Astros', 'Kansas City Royals', 'Los Angeles Dodgers', 'Milwaukee Brewers', 
        #  'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics', 'Philadelphia Phillies', 
        #  'Pittsburgh Pirates', 'San Diego Padres', 'Seattle Mariners', 'San Francisco Giants', 'St. Louis Cardinals', 
        #  'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals', 'WP < .500', 'WP >= .500', 
        #  'Night', 'Day', 'Open', 'Dome', 'Retract', 'Grass', 'Artif. Turf', 'LAA-Angel Stad', 'ARI-Chase Field', 
        #  'Muncy Bank BP', 'STL-Busch Stad 3', 'NYM-Citi Field', 'DET-Comerica Pk', 'CHW-Guaranteed', 'HOU-MinuteMaidPk', 
        #  'BOS-Fenway Pk', 'CIN-GreatAmer BP', 'CLE-Progressive', 'MIA-loanDepot pk', 'MIL-Am Fam Field', 'WSN-Natls Park', 
        #  'OAK-Oakland Col.', 'BAL-Camden Yards', 'SFG-Oracle Park', 'SDP-Petco Pk', 'PIT-PNC Pk', 'KCR-KauffmanStad', 
        #  'SEA-T-Mobile Pk', 'TOR-Rogers Ctr', 'ATL-Truist Pk', 'MIN-Target Field', 'TBR-TropicanaFld', 'CHC-Wrigley Fld', 
        #  'NYY-Yankee Stad3', 'TEX-GlbLifeField']

        # Acces example:
        #    data.xs('vs LHP', level=1)['AB']

    @staticmethod
    def fetch_batting_splits_leaderboards(player_bbref: str, season:int):
        data = pyb.get_splits(playerid=player_bbref, year=season)
        return data 
