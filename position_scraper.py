import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import math

# NaN is set for any value not in the table

# prints entire pandas table
pd.set_option('display.max_columns', None)


class Scraper:
    ################## Parameters for scraping team data ##################
    # first 32 represent team stubs. the rest are team ID's (tmID) for teams who changed their names
    team_stubs = {'buf': 1, 'mia': 2, 'nwe': 3, 'nyj': 4, 'htx': 5, 'clt': 6, 'jax': 7, 'oti': 8, 'cle': 9, 'pit': 10,
                  'cin': 11, 'rav': 12, 'kan': 13, 'sdg': 14, 'rai': 15, 'den': 16, 'nyg': 17, 'dal': 18, 'was': 19,
                  'phi': 20, 'car': 21, 'nor': 22, 'tam': 23, 'atl': 24, 'gnb': 25, 'min': 26, 'chi': 27, 'det': 28,
                  'sea': 29, 'crd': 30, 'ram': 31, 'sfo': 32, '2tm': -1, '3tm': -1, 'hou': 5, 'ind': 6, 'ten': 8,
                  'oak': 15, 'ari': 30, 'stl': 31, 'bal': 12, 'lac': 14, 'lvr': 15, 'lar': 31}

    # Names of the tables with values to be scraped
    tables_to_scrape = ["fantasy", "rushing_and_receiving", "receiving_and_rushing", "combine", "passing",
                        "passing_advanced"]
    # list of players that have already been scraped
    parsed_players = []
    # any errors will be recorded as [player, table] or ALL if rejected
    errors = []

    ################## Data ##################
    team_stats = []
    fantasy = []
    rushing_and_receiving = []
    combine = []
    passing = []
    adj_passing = []
    combined = []
    yearlyStats = []

    # iteration data. If a player has an error while scraping they will not be added
    current_fantasy = []
    current_rush_receive = []
    current_combine = []
    current_passing = []
    current_adj_pass = []
    current_combined = []

    # Change years to scrape here for testing
    def __init__(self, year_start=2000, year_end=2020, max_players=200):
        # self.year_start and year_start are not the same.  Best when to init a self value to use the same name for both
        # this makes it easier to identify and read code. Self is for that instance of the object. With out the self.
        # tag the variable is local to the function

        self.year_start = year_start
        self.year_end = year_end
        self.max_players = max_players
        self.clearTables()

    def pullPosPlayer(self):
        """ This is the main scraping Subroutine. Will scrape the top max_players from year_start to year_end
        and place them in the data arrays that can be accessed with the getters."""
        for year in range(self.year_start, self.year_end):
            print('             ', year, '\n')
            player_list = self.scrapePositionPlayer(year)

            # This is where you can declare a subset of the max_players scraped for testing purposes
            shortList = player_list[:]
            for player in shortList:
                name = player[0]
                if name not in self.parsed_players:

                    self.parsed_players.append(name)
                    try:
                        self.scrapePlayerStatTables(player)
                        self.addTables()
                    except Exception as e:
                        self.errors.append([name, "Error {}".format(e)])

        print('errors', len(self.errors), self.errors)

    def scrapePositionPlayer(self, year):
        """Will get the first max_players from any given fantasy year. Players that have already been scraped
        will be ignored. Returns a list of [playerName, stub, position]"""
        index = 0
        print("Getting player list....")
        # Make the request to a url
        r = requests.get('https://www.pro-football-reference.com/years/' + str(year) + '/fantasy.htm')
        # Create soup from content of request
        c = r.content

        soup = bs(c, 'html.parser')

        parsed_table = soup.find_all('table')[0]
        column_names = soup.find_all('tr', class_='')[0]
        players = soup.find_all('tr', class_='')[1:]

        player_list = []
        subset = players[:]
        for i, player in enumerate(subset):
            dat = player.find('td', attrs={'data-stat': 'player'})
            name = dat.a.get_text()
            stub = dat.a.get('href')
            pos = player.find('td', attrs={'data-stat': 'fantasy_pos'}).get_text().lower()
            if len(pos) == 2:
                player_list.append([name, pos, stub])
            if i + 1 >= self.max_players:
                break

        return player_list

    def scrapePlayerStatTables(self, player):
        """For each player in the player table, this subroutine will look for each table in the tables_to_scrape.
        If data exists, the data will be scraped into the appropriate data table"""

        name = player[0]
        pos = player[1].lower()
        stub = player[2]
        pid = len(self.parsed_players)
        years_to_scrape = []
        current_table = []

        self.current_fantasy = []
        self.current_rush_receive = []
        self.current_combine = []
        self.current_passing = []
        self.current_adj_pass = []
        self.current_combined = []
        print(name, pos)

        # Make the request to a url
        r = requests.get('https://www.pro-football-reference.com' + str(stub))
        # Create soup from content of request
        c = r.content
        soup = bs(c, 'html.parser')
        d = str(soup).replace("<!--", "").replace("-->", "")
        soup = bs(d, 'html.parser')
        tables = soup.find_all('table')

        # Iterates through all tables
        for i, table in enumerate(self.tables_to_scrape):
            try:
                tables = soup.find_all('table', id=table)[0].find_all('tbody')
            except:
                if i == 1 and (pos == 'wr' or pos == 'te'):
                    continue
                elif i == 2 and (pos == 'rb' or pos == 'qb'):
                    continue
                elif i == 4 or i == 5 and pos != 'qb':
                    continue
                else:
                    if i == 3:
                        self.current_combine = [[pid, name, 0, pos, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                                                 np.nan, np.nan]]
                    self.errors.append([name, table])
                continue
            for j, row in enumerate(tables[0].children):
                if j % 2 != 0:
                    current_table = []

                if len(row) < 5:  # controls for years missed
                    continue
                year = row.find_all('a')[0].get_text()

                try:
                    year = int(year)
                except:
                    continue
                if (year < self.year_start or year > self.year_end) and i != 3:
                    continue
                current_table.append(year)
                for item in row.find_all('td'):
                    val = str(item.get_text()).replace('%', '')
                    if len(val) == 0:
                        val = np.nan
                    current_table.append(val)

                x = len(current_table)

                # Fantasy
                if i == 0:

                    ftid = len(self.fantasy) - 1 + len(self.current_fantasy)
                    current_table.insert(0, ftid)
                    current_table[4] = pos

                    # Checks for null value in fantasy pts.
                    try:
                        int(current_table[5])
                    except:
                        current_table[5] = 0

                    # Checks for null value in Games Played. Indicates player Did not play at all so data can be ignored.
                    try:
                        int(current_table[3])
                        self.current_fantasy.append(current_table)
                        years_to_scrape.append(year)
                        self.current_combined.append([pid, '', current_table[1], '', '', '', current_table[0]])
                    except:
                        current_table = []

                    try:
                        ytid = len(self.yearlyStats) - 1
                        # print(stub[9:-4], year, pid, ytid)
                        current_yearly_stats = self.getPlayerYearlyStats(stub[9:-4], year, pid, ytid, pos)
                        # print(current_yearly_stats)
                        for stat in current_yearly_stats:
                            self.yearlyStats.append(stat)
                    except:
                        self.errors.append([name, year + 'stats'])

                    #  rushing and receiving
                elif i == 1:
                    if x < 32:
                        current_table.append(0)
                    ruretid = len(self.rushing_and_receiving) - 1 + (len(self.current_rush_receive))
                    if year in years_to_scrape:
                        current_table.insert(0, ruretid)
                    current_table[4] = pos
                    current_table[3] = self.team_stubs[current_table[3].lower()]
                    self.current_rush_receive.append(current_table)

                    # receiving and rushing
                elif i == 2:
                    if year in years_to_scrape:
                        rerutid = len(self.rushing_and_receiving) - 1 + (len(self.current_rush_receive))
                        current_table.insert(0, rerutid)
                        current_table[4] = pos
                        current_table[3] = self.team_stubs[current_table[3].lower()]
                        self.current_rush_receive.append(self.fix_rec(current_table))

                        # combine
                elif i == 3:
                    current_table.insert(0, pid)  # pid based on parsed players
                    current_table.insert(1, name)  # check
                    self.current_combine.append(current_table)

                    # passing
                elif i == 4:
                    if year in years_to_scrape and pos == 'qb':

                        ptid = len(self.passing) - 1 + len(self.current_passing)
                        current_table.insert(0, ptid)
                        if current_table[30] is np.nan:
                            current_table[30] = 0
                        if current_table[31] is np.nan:
                            current_table[31] = 0
                        current_table[3] = self.team_stubs[current_table[3].lower()]
                        current_table[4] = pos
                        self.current_passing.append(current_table)

                        # adjusted passing
                elif i == 5:
                    if year in years_to_scrape:
                        aptid = len(self.adj_passing) - 1 + len(self.current_adj_pass)
                        current_table.insert(0, aptid)
                        current_table[3] = self.team_stubs[current_table[3].lower()]
                        current_table[4] = pos
                        self.current_adj_pass.append(current_table)

        self.createCombined()

    # NOTE: This only works with RB, need to generalize to QB / WR / TE

    def getPlayerYearlyStats(self, stub, year, pid, ytid, pos):
        final_stats = []
        current_yearly_stats = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        current_table = [ytid, pid]
        # Make the request to a url
        r = requests.get('https://www.pro-football-reference.com/players/' + str(stub) + '/gamelog/' + str(year))
        # Create soup from content of request
        c = r.content

        soup = bs(c, 'html.parser')
        # tables = soup.find_all('table')
        tables = soup.find_all('table', id="stats")[0].find_all('tbody')
        for j, row in enumerate(tables[0].children):
            if j % 2 != 0:
                ytid = ytid + 1
                current_table = [ytid, pid]
                continue
            # print(j, row)
            for i, item in enumerate(row.find_all('td')):
                # print(item)
                if i < 25:
                    val = str(item.get_text()).replace('%', '')
                    # print(val)
                    if i == 0:
                        val = year
                    elif i == 4 or i == 6:
                        val = self.team_stubs[val.lower()]
                    elif i == 5:
                        try:
                            if str(val) == '@':
                                val = 1
                            else:
                                val = 0
                        except:
                            val = 0
                    elif i == 7:
                        if val[0] == 'L':
                            val = 0
                        elif val[0] == 'W':
                            val = 1
                        else:  # Tie
                            val = 0.5
                    elif i == 8:
                        try:
                            if str(val) == '*':
                                val = 1
                            else:
                                val = 0
                        except:
                            val = 0
                    elif len(val) == 0:
                        val = 0
                    current_table.append(val)
            current_yearly_stats[0] = current_table[:11]
            if pos == 'wr':
                current_yearly_stats[2] = current_table[11:18]
                current_rushing = current_table[18:22]
                # This handles the edge case where a receiver doesn't have rushing columns
                if len(current_rushing) == 4:
                    current_yearly_stats[1] = current_rushing
                # print(current_yearly_stats[2])
                # print(current_yearly_stats[1])
            elif pos == 'rb':
                current_yearly_stats[1] = current_table[11:15]
                current_yearly_stats[2] = current_table[15:22]
            elif pos == 'te':
                current_yearly_stats[2] = current_table[11:18]
            elif pos == 'qb':
                current_yearly_stats[3] = current_table[11:22]
                current_yearly_stats[1] = current_table[22:26]

            temp = []
            for values in current_yearly_stats:
                for val in values:
                    temp.append(val)
            final_stats.append(temp)

        return final_stats

    def scrapeTeams(self):
        """ scrapes data about yearly team performance"""
        tablekey = 1
        teams_to_scrape = list(self.team_stubs.keys())[:32]

        # Allows for choosing a subset of teams for troubleshooting
        team_subset = teams_to_scrape[:]
        for j, team in enumerate(team_subset):
            print(j + 1, team)
            # for year in range(self.year_start, self.year_end + 1):
            for year in range(self.year_start, self.year_end):

                print('https://www.pro-football-reference.com/teams/' + str(team) + '/' + str(year) + '.htm')
                # Make the request to a url
                r = requests.get('https://www.pro-football-reference.com/teams/' + str(team) + '/' + str(year) + '.htm')
                # Create soup from content of request
                c = r.content
                soup = bs(c, 'html.parser')
                # For teams that weren't created
                try:
                    tables = soup.find_all('table', id='team_stats')[0]
                except:
                    continue
                try:  # try statement to catch an error if the index is out of range for this call to this line of code
                    tables = soup.find_all('table', id='team_stats')[0]
                except Exception as e:
                    print("Error {}".format(e))
                # print(tables)
                print('https://www.pro-football-reference.com/teams/' + str(team) + '/' + str(year) + '.htm')
                rows = tables.find_all('tbody')
                for i, row in enumerate(rows[0].children):
                    if i % 2 == 0:
                        current = []
                        current.append(j + 1)  # team id
                        current.append(year)
                        row_name = row.find('th').get_text()
                        current.append(row_name)

                        for item in row.find_all('td'):
                            val = str(item.get_text().replace('Own', ''))
                            if len(val) == 0:
                                val = np.nan
                            current.append(val)
                        current.insert(0, tablekey)
                        tablekey += 1
                        self.team_stats.append(current)

        team_pd = pd.DataFrame(self.team_stats[2:], columns=self.team_stats[1])

    def fix_rec(self, input_receiving_table):
        """turns the receiving rushing table into the rushing receiving table"""
        corrected = (input_receiving_table[:8] + input_receiving_table[19:27] + input_receiving_table[
                                                                                8:19] + input_receiving_table[27:])
        return corrected

    def createCombined(self):
        """creates the combined table for linking data for players together"""

        for record in self.current_combined:
            year = record[2]
            for val in self.current_rush_receive:
                if val[1] == year:
                    record[5] = val[0]
                    break
            for val in self.current_rush_receive:
                if val[1] == year:
                    record[1] = val[3]
                    break
            for val in self.current_passing:
                if val[1] == year:
                    record[3] = val[0]
                    break
            for val in self.current_adj_pass:
                if val[1] == year:
                    record[4] = val[0]
                    break

    def printRecords(self):
        """prints all records if they exist, mostly for testing"""
        if len(self.fantasy) > 0:
            print("fantasy")
            print(self.fantasy)
        if len(self.rushing_and_receiving) > 0:
            print("rushing and receiving")
            print(self.rushing_and_receiving)
        if len(self.combine) > 0:
            print("combine")
            print(self.combine)
        if len(self.passing) > 0:
            print("passing")
            print(self.passing)
        if len(self.adj_passing) > 0:
            print("adjusted passing")
            print(self.adj_passing)

    def addTables(self):
        """After tables for a player have been scraped, as long as there are no errors, this will add scraped tables
        to the data section"""
        for val in self.current_fantasy:
            self.fantasy.append(val)
        for val in self.current_rush_receive:
            self.rushing_and_receiving.append(val)
        for val in self.current_passing:
            self.passing.append(val)
        for val in self.current_adj_pass:
            self.adj_passing.append(val)
        for val in self.current_combine:
            self.combine.append(val)
        for val in self.current_combined:
            self.combined.append(val)

    # Getters - returns data frames of data section lists
    def getFantasyDataFrame(self):
        return pd.DataFrame(self.fantasy[2:], columns=self.fantasy[1])

    def getRushRecDataFrame(self):
        return pd.DataFrame(self.rushing_and_receiving[2:], columns=self.rushing_and_receiving[1])

    def getPassingDataFrame(self):
        return pd.DataFrame(self.passing[2:], columns=self.passing[1])

    def getAdjPassingDataFrame(self):
        return pd.DataFrame(self.adj_passing[2:], columns=self.adj_passing[1])

    def getcombineDataFrame(self):
        return pd.DataFrame(self.combine[2:], columns=self.combine[1])

    def getCombinedDataFrame(self):
        return pd.DataFrame(self.combined[2:], columns=self.combined[1])

    def getTeamStatsDataFrame(self):
        return pd.DataFrame(self.team_stats[2:], columns=self.team_stats[1])

    def getYearlyStatsDataFrame(self):
        return pd.DataFrame(self.yearlyStats[2:], columns=self.yearlyStats[1])

    def clearTables(self):
        """Resets data to baseline"""
        self.fantasy = [['Fantasy'], ['ftid', 'Year', 'Age', 'G', 'FantPos', 'FantPt', 'VBD', 'PosRank', 'OvRank']]
        self.rushing_and_receiving = [['Rushing_Receiving'],
                                      ['ruretid', 'year', 'age', 'TmID', 'Pos', 'No.', 'G', 'GS', 'Rush', 'RUSHYds',
                                       'RUSHTD',
                                       'RUSH1D', 'RUSHLng', 'RushYA', 'RUSHYG', 'RUSHAG', 'TGT', 'Rec', 'RECYds',
                                       'YRec',
                                       'RECTD', 'REC1D', 'RECLng', 'RecG', 'RECYG', 'CtchPct',
                                       'YTgt', 'Touch', 'YTch', 'YScm', 'RRTD', 'Fmb', 'AV']]
        self.combine = [['Player'],
                        ['pid', 'name', 'Year', 'Pos', 'Ht', 'Wt', '40yd', 'Bench', 'Broad_Jump', 'Shuttle', '3Cone',
                         'Vertical']]
        self.passing = [['Passing'],
                        ['ptid', 'Year', 'Age', 'TmID', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Cmp', 'Att', 'Cmp%', 'Yds',
                         'TD', 'TD%', 'Int', 'Int%', '1D', 'Lng', 'YA', 'AYA', 'YC', 'YG', 'Rate', 'QBR', 'Sk',
                         'SkYdsLost',
                         'NYA', 'ANYA', 'Sk%', '4QC', 'GWD', 'AV']]
        self.adj_passing = [['Adjusted_Passing'],
                            ['aptid', 'Year', 'Age', 'TmID', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Att', 'YA+', 'NYA+',
                             'AYA+',
                             'ANYA+', 'Cmp%+', 'TD%+', 'Int%+', 'Sack%+', 'Rate+']]
        self.combined = [['Combined'], ['pid', 'ttid', 'year', 'ptid', 'aptid', 'ruretid', 'ftid']]
        self.team_stats = [['Team_Stats'],
                           ['ttid', 'TmID', 'year', 'Player', 'PF', 'Yds', 'Ply', 'YP', 'TO', 'FL', 'Tot1stD', 'Cmp',
                            'PASSAtt', 'PASSYds',
                            'PASSTD', 'Int', 'NYA', 'Pass1stD', 'RUSHAtt', 'RUSHYds', 'RUSHTD', 'RUSHYA', 'RUSH1stD',
                            'Pen', 'PENYds', '1stPy',
                            '#Dr',
                            'Sc%', 'TO%', 'Start', 'Time', 'Plays', 'AVGYds', 'AVGPts']]
        self.yearlyStats = [["Yearly_Stats"],
                            ['ytid', 'pid', 'Year', 'G#', 'Week', 'Age', 'TmID', 'away', 'Opp_TmID', 'Result', 'GS',
                             'Rush_Att',
                             'Rush_Yds', 'Rush_YA', 'Rush_TD', 'Tgt', 'Rec', 'Rec_Yds', 'RecYR', 'Rec_TD', 'Ctch%',
                             'YTgt',
                             'cmp', 'pass_Att', 'Cmp%', 'pass_Yds', 'pass_TD', 'Int', 'pass_Rate', 'Sack', 'Sack_yds',
                             'Pass_YA', 'PASS_AYA']]

