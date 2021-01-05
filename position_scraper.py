import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

# NaN is set for any value not in the table

# prints entire pandas table
pd.set_option('display.max_columns', None)


class Scraper:

    ################## Hyper Parameters - Parameters set for testing ##################
    year_start = 0
    year_end = 0
    max_players = 200   # DEFAULT - 200. Players within the top X spots get scraped

    ################## Parameters for scraping team data ##################
    # first 32 represent team stubs. the rest are team ID's (tmID) for teams who changed their names
    team_stubs = {'buf': 1, 'mia': 2, 'nwe': 3, 'nyj': 4, 'htx': 5, 'clt': 6, 'jax': 7, 'oti': 8, 'cle': 9, 'pit': 10,
                  'cin': 11, 'rav': 12, 'kan': 13, 'sdg': 14, 'rai': 15, 'den': 16, 'nyg': 17, 'dal': 18, 'was': 19,
                  'phi': 20, 'car': 21, 'nor': 22, 'tam': 23, 'atl': 24, 'gnb': 25, 'min': 26, 'chi': 27, 'det': 28,
                  'sea': 29, 'crd': 30, 'ram': 31, 'sfo': 32, '2tm': -1, '3tm': -1, 'hou': 5, 'ind': 6, 'ten':8,
                  'oak': 15, 'ari': 30, 'stl': 31, 'bal': 12}


    # Names of the tables with values to be scraped
    tables_to_scrape = ["fantasy", "rushing_and_receiving", "receiving_and_rushing", "combine", "passing",
                        "passing_advanced"]
    # list of players that have already been scraped
    parsed_players = []
    # any errors will be recorded as [player, table] or ALL if rejected
    errors = []
    min_games = 4

    ################## Data ##################
    team_stats = []
    fantasy = []
    rushing_and_receiving = []
    combine = []
    passing = []
    adj_passing = []
    combined = []

    # iteration data. If a player has an error while scrapin they will not be added
    current_fantasy = []
    current_rush_receive = []
    current_combine = []
    current_passing = []
    current_adj_pass = []
    current_combined = []

    # Change years to scrape here for testing
    def __init__(self, year_start=2010, year_end=2019, max_players=200):

        self.year_start = year_start    # self.year_start and year_start are not the same.  Best when to init a self value to use the same name for both
        self.year_end = year_end        # this makes it easier to identify and read code. Self is for that instance of the object. With out the self.
        self. max_players = max_players # tag the variable is local to the function
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
                    except:
                        self.errors.append([name, 'ALL'])

        print('errors', self.errors)

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

        for i, player in enumerate(players):
            dat = player.find('td', attrs={'data-stat': 'player'})
            name = dat.a.get_text()
            stub = dat.a.get('href')
            pos = player.find('td', attrs={'data-stat': 'fantasy_pos'}).get_text()
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
                        self.current_fantasy.append(current_table)
                        years_to_scrape.append(year)
                        self.current_combined.append([pid, current_table[1], '',  '', '', current_table[0]])

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
                            self.current_passing.append(current_table)

                    # adjusted passing
                    elif i == 5:
                        if year in years_to_scrape:
                            aptid = len(self.adj_passing) - 1 + len(self.current_adj_pass)
                            current_table.insert(0, aptid)
                            current_table[3] = self.team_stubs[current_table[3].lower()]
                            self.current_adj_pass.append(current_table)

        self.createCombined()


    def scrapeTeams(self):
        """ scrapes data about yearly team performance"""
        teams_to_scrape = list(self.team_stubs.keys())[:32]
        for j, team in enumerate(teams_to_scrape):
            print(j + 1, team)
            for year in range(self.year_start, self.year_end + 1):
                print('https://www.pro-football-reference.com/teams/' + str(team) + '/' + str(year) + '.htm')
                # Make the request to a url
                r = requests.get('https://www.pro-football-reference.com/teams/' + str(team) + '/' + str(year) + '.htm')
                # Create soup from content of request
                c = r.content
                soup = bs(c, 'html.parser')
                tables = soup.find_all('table', id='team_stats')[0]
                try:  # try statement to catch an error if the index is out of range for this call to this line of code
                    tables = soup.find_all('table', id='team_stats')[0]
                except Exception as e:
                    print("Error {}".format(e))
                # print(tables)
                rows = tables.find_all('tbody')
                for i, row in enumerate(rows[0].children):
                    if i % 2 != 0:
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
                        self.team_stats.append(current)

        team_pd = pd.DataFrame(self.team_stats[2:], columns=self.team_stats[1])
        print(team_pd)

    def fix_rec(self, input_receiving_table):
        """turns the receiving rushing table into the rushing receiving table"""
        corrected = (input_receiving_table[:8] + input_receiving_table[19:27] + input_receiving_table[8:19] + input_receiving_table[27:])
        return corrected

    def createCombined(self):
        """creates the combined table for linking data for players together"""
        for record in self.current_combined:
            year = record[1]
            for val in self.current_rush_receive:
                if val[1] == year:
                    record[4] = val[0]
                    break
            for val in self.current_passing:
                if val[1] == year:
                    record[2] = val[0]
                    break
            for val in self.current_adj_pass:
                if val[1] == year:
                    record[3] = val[0]
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
        self.combine.append(self.current_combine)

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

    def clearTables(self):
        """Resets data to baseline"""
        self.fantasy = [['Fantasy'], ['ftid', 'Year', 'Age', 'G', 'FantPos', 'FantPt', 'VBD', 'PosRank', 'OvRank']]
        self.rushing_and_receiving = [['Rushing and Receiving'],
                                 ['ruretid', 'Year', 'Age', 'TmID', 'Pos', 'No.', 'G', 'GS', 'Rush', 'Yds', 'TD', '1D',
                                  'Lng',
                                  'Y/A', 'Y/G', 'A/G', 'Tgt', 'Rec', 'Yds', 'Y/R', 'TD', '1D', 'Lng', 'R/G', 'Y/G',
                                  'Ctch%',
                                  'Y/Tgt', 'Touch', 'Y/Tch', 'YScm', 'RRTD', 'Fmb', 'AV']]
        self.combine = [['Combine'],
                   ['pid', 'Year', 'Pos', 'Ht', 'Wt', '40yd', 'Bench', 'Broad Jump', 'Shuttle', '3Cone', 'Vertical']]
        self.passing = [['Passing'],
                   ['ptid', 'Year', 'Age', 'TmID', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Cmp', 'Att', 'Cmp%', 'Yds', 'TD',
                    'TD%',
                    'Int', 'Int%', '1D', 'Lng', 'Y/A', 'AY/A', 'Y/C', 'Y/G', 'Rate', 'QBR', 'Sk', 'Yds', 'NY/A',
                    'ANY/A',
                    'Sk%', '4QC', 'GWD', 'AV']]
        self.adj_passing = [['Adjusted Passing'],
                       ['aptid', 'Year', 'Age', 'TmID', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Att', 'Y/A+', 'NY/A+', 'AY/A+',
                        'ANY/A+', 'Cmp%+', 'TD%+', 'Int%+', 'Sack%+', 'Rate+']]
        self.combined = [['Combined'], ['pid', 'year', 'ptid', 'aptid', 'ruretid', 'ftid']]
        self.team_stats = [['Team Stats'],
                      ['tid', 'year', 'Player', 'PF', 'Yds', 'Ply', 'Y/P', 'TO', 'FL', '1stD', 'Cmp', 'Att', 'Yds',
                       'TD', 'Int', 'NY/A', '1stD', 'Att', 'Yds', 'TD', 'Y/A', '1stD', 'Pen', 'Yds', '1stPy', '#Dr',
                       'Sc%', 'TO%', 'Start', 'Time', 'Plays', 'Yds', 'Pts']]
