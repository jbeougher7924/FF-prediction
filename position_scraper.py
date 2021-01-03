import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

# prevented rb/wr/te from having a passing table
# NaN is set for any value not in the table


# prints entire pandas table
pd.set_option('display.max_columns', None)


class Scraper:

    year_start = 0
    year_end = 0
    max_players = 200   # change this to 200

    parsed_players = []
    teams = {'buf': 1, 'mia': 2, 'nwe': 3, 'nyj': 4, 'htx': 5, 'clt': 6, 'jax': 7, 'oti': 8, 'cle': 9, 'pit': 10, 'cin': 11, 'rav': 12, 'kan': 13, 'sdg': 14, 'rai': 15, 'den': 16, 'nyg': 17, 'dal': 18, 'was': 19, 'phi': 20, 'car': 21, 'nor': 22, 'tam': 23, 'atl': 24, 'gnb': 25, 'min': 26, 'chi': 27, 'det': 28, 'sea': 29, 'crd':30, 'ram':31, 'sfo':32, '2tm': -1, '3tm': -1}

    tables_to_scrape = ["fantasy", "rushing_and_receiving", "receiving_and_rushing", "combine", "passing",
                        "passing_advanced"]

    errors = []
    min_games = 4

    team_stats = []
    fantasy = []
    rushing_and_receiving = []
    combine = []
    passing = []
    adj_passing = []
    combined = []

    current_fantasy = []
    current_rush_receive = []
    current_combine = []
    current_passing = []
    current_adj_pass = []
    current_combined = []

    def __init__(self, ystart=2010, yend=2019):

        self.year_start = ystart
        self.year_end = yend
        self.clearTables()

    def pullPosPlayer(self):
        for year in range(self.year_start, self.year_end):
            print('             ', year, '\n')
            player_list = self.getPosPlayer(year)

            shortList = player_list[:]
            for player in shortList:
                name = player[0]
                if name not in self.parsed_players:

                    self.parsed_players.append(name)
                    try:
                        self.getPlayerStatTables(player)
                        self.addTables()
                    except:
                        self.errors.append([name, 'ALL'])

        print('errors', self.errors)

    def getPosPlayer(self, year):
        index = 0
        print("Getting player list....")
        # print('https://www.pro-football-reference.com/years/' + str(year) + '/fantasy.htm')
        # Make the request to a url
        r = requests.get('https://www.pro-football-reference.com/years/' + str(year) + '/fantasy.htm')
        # Create soup from content of request
        c = r.content

        soup = bs(c, 'html.parser')

        parsed_table = soup.find_all('table')[0]
        # print(parsed_table)

        column_names = soup.find_all('tr', class_='')[0]
        players = soup.find_all('tr', class_='')[1:]

        player_list = []

        for i, player in enumerate(players):
            dat = player.find('td', attrs={'data-stat': 'player'})
            name = dat.a.get_text()
            stub = dat.a.get('href')
            pos = player.find('td', attrs={'data-stat': 'fantasy_pos'}).get_text()
            # print(i+1, name, pos, stub)
            if len(pos) == 2:
                player_list.append([name, pos, stub])
            if i + 1 >= self.max_players:
                break

        return player_list

    def getPlayerStatTables(self, player):
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
        # d = str(soup).replace("<!--","").replace("-->","").replace("receiving_and_rushing", "rushing_and_receiving")
        d = str(soup).replace("<!--", "").replace("-->", "")
        soup = bs(d, 'html.parser')
        # print(soup.prettify)
        tables = soup.find_all('table')

        # print(tables)

        # Iterates through all tables
        for i, table in enumerate(self.tables_to_scrape):
            # print(table)
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
            # print('tables', tables)

            for j, row in enumerate(tables[0].children):
                if j % 2 != 0:
                    current_table = []
                    # print(table, 'j',j, j//2)

                    if len(row) < 5:  # controls for years missed
                        continue
                    # print(j, row)
                    year = row.find_all('a')[0].get_text()
                    try:
                        year = int(year)
                    except:
                        continue
                    if (year < self.year_start or year > self.year_end) and i != 3:
                    # if (year < 2010 or year > 2019) and i != 3:
                        continue
                    current_table.append(year)
                    # print(year)
                    for item in row.find_all('td'):
                        val = str(item.get_text()).replace('%', '')
                        if len(val) == 0:
                            val = np.nan
                        current_table.append(val)

                    x = len(current_table)

                    # Fantasy
                    if i == 0:

                        # print(year, j//2)
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
                            self.current_rush_receive.append(current_table)

                    # receiving and rushing
                    elif i == 2:
                        if year in years_to_scrape:
                            rerutid = len(self.rushing_and_receiving) - 1 + (len(self.current_rush_receive))
                            current_table.insert(0, rerutid)
                            current_table[4] = pos
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
                            self.current_passing.append(current_table)

                    # adjusted passing
                    elif i == 5:
                        if year in years_to_scrape:
                            aptid = len(self.adj_passing) - 1 + len(self.current_adj_pass)
                            current_table.insert(0, aptid)
                            self.current_adj_pass.append(current_table)

        self.createCombined()


    def scrapeTeams(self):
        teams_to_scrape = list(self.teams.keys())[:33]
        for j, team in enumerate(teams_to_scrape):
            print(j + 1, team)
            for year in range(self.year_start, self.year_end):
                print('https://www.pro-football-reference.com/teams/' + str(team) + '/' + str(year) + '.htm')
                # Make the request to a url
                r = requests.get('https://www.pro-football-reference.com/teams/' + str(team) + '/' + str(year) + '.htm')
                # Create soup from content of request
                c = r.content
                soup = bs(c, 'html.parser')
                tables = soup.find_all('table', id='team_stats')[0]
                # print(tables)
                rows = tables.find_all('tbody')
                for i, row in enumerate(rows[0].children):
                    if i % 2 != 0:
                        current = []
                        current.append(j + 1)  # team id
                        current.append(year)
                        # print(row)
                        row_name = row.find('th').get_text()
                        # print(row_name)
                        current.append(row_name)

                        for item in row.find_all('td'):
                            val = str(item.get_text().replace('Own', ''))
                            # print(val)
                            if len(val) == 0:
                                val = np.nan
                            current.append(val)
                        self.team_stats.append(current)

        team_pd = pd.DataFrame(self.team_stats[2:], columns=self.team_stats[1])
        print(team_pd)

    def fix_rec(self, input_receiving_table):
        corrected = (input_receiving_table[:8] + input_receiving_table[19:27] + input_receiving_table[8:19] + input_receiving_table[27:])
        return corrected

    def createCombined(self):
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

    def getFantasyTable(self):
        return pd.DataFrame(self.fantasy[2:], columns=self.fantasy[1])

    def getRushRecTable(self):
        return pd.DataFrame(self.rushing_and_receiving[2:], columns=self.rushing_and_receiving[1])

    def getPassingTable(self):
        return pd.DataFrame(self.passing[2:], columns=self.passing[1])

    def getAdjPassingTable(self):
        return pd.DataFrame(self.adj_passing[2:], columns=self.adj_passing[1])

    def getcombineTable(self):
        return pd.DataFrame(self.combine[2:], columns=self.combine[1])

    def getCombinedTable(self):
        return pd.DataFrame(self.combined[2:], columns=self.combined[1])

    def getTeamStatsTable(self):
        return pd.DataFrame(self.team_stats[2:], columns=self.team_stats[1])

    def clearTables(self):
        self.fantasy = [['Fantasy'], ['ftid', 'Year', 'Age', 'G', 'FantPos', 'FantPt', 'VBD', 'PosRank', 'OvRank']]
        self.rushing_and_receiving = [['Rushing and Receiving'],
                                 ['ruretid', 'Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'Rush', 'Yds', 'TD', '1D',
                                  'Lng',
                                  'Y/A', 'Y/G', 'A/G', 'Tgt', 'Rec', 'Yds', 'Y/R', 'TD', '1D', 'Lng', 'R/G', 'Y/G',
                                  'Ctch%',
                                  'Y/Tgt', 'Touch', 'Y/Tch', 'YScm', 'RRTD', 'Fmb', 'AV']]
        self.combine = [['Combine'],
                   ['pid', 'Year', 'Pos', 'Ht', 'Wt', '40yd', 'Bench', 'Broad Jump', 'Shuttle', '3Cone', 'Vertical']]
        self.passing = [['Passing'],
                   ['ptid', 'Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Cmp', 'Att', 'Cmp%', 'Yds', 'TD',
                    'TD%',
                    'Int', 'Int%', '1D', 'Lng', 'Y/A', 'AY/A', 'Y/C', 'Y/G', 'Rate', 'QBR', 'Sk', 'Yds', 'NY/A',
                    'ANY/A',
                    'Sk%', '4QC', 'GWD', 'AV']]
        self.adj_passing = [['Adjusted Passing'],
                       ['aptid', 'Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Att', 'Y/A+', 'NY/A+', 'AY/A+',
                        'ANY/A+', 'Cmp%+', 'TD%+', 'Int%+', 'Sack%+', 'Rate+']]
        self.combined = [['Combined'], ['pid', 'year', 'ptid', 'aptid', 'ruretid', 'ftid']]
        self.team_stats = [['Team Stats'],
                      ['tid', 'year', 'Player', 'PF', 'Yds', 'Ply', 'Y/P', 'TO', 'FL', '1stD', 'Cmp', 'Att', 'Yds',
                       'TD', 'Int', 'NY/A', '1stD', 'Att', 'Yds', 'TD', 'Y/A', '1stD', 'Pen', 'Yds', '1stPy', '#Dr',
                       'Sc%', 'TO%', 'Start', 'Time', 'Plays', 'Yds', 'Pts']]
