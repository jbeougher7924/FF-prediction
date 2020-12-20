import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd

# Important constants
min_total_yards = 250
year_start = 2010
year_end = 2011

# tables to collect
wanted_tables = []

# data
Rush_Rec_table = [['Rush and Receiving Table'],
                  ['arrtid', 'pid', 'Name', 'Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'Rush', 'Yds', 'TD', '1D',
                   'Lng', 'Y/A', 'Y/G', 'A/G', 'Tgt', 'Rec', 'Yds', 'Y/R', 'TD', '1D', 'Lng', 'R/G', 'Y/G', 'Ctch%',
                   'Y/Tgt', 'Touch', 'Y/Tch', 'YScm', 'RRTD', 'Fmb']]
Fantasy_Table = [['Fantasy Table'],
                 ['ftid', 'pid', 'Name', 'Year', 'Age', 'G', 'FantPos', 'FantPt', 'VBD', 'PosRank', 'OvRank']]
Statistics_Table = [['Statistics Table'], ['pid', 'year', 'arrtid', 'ftid']]

# caught errors
errorList = []

# This value keeps track of years with the minimum completions and starts
# only fantasy pts from these years will be collected
current_years = []
pulled = []
pname = ""
pid = 0
position = None  # based off fantasy positin


class Scraper:

    def __init__(self, minyds=250, ystart=2010, yend=2011):
        self.min_total_yards = minyds
        self.year_start = ystart
        self.year_end = yend

    def pullPosPlayer(self):

        for year in range(year_start, year_end):
            print('             ', year, '\n')
            players = self.getPosPlayer(year)

            for entry in players:
                self.pname = entry[0]

                if not pulled.__contains__(pname):
                    print('Processing:            ', pname)
                    pulled.append(pname)
                    pid = self.getpid()
                    address = str(entry[1])

                    playertables = self.getPlayerStatTables(address)

    def getPosPlayer(self, year):
        """
        In: a year
        Out: a list of all players that had > minimum yards from scrimmage
        """
        allplayers = []
        index = 0
        r = requests.get('https://pro-football-reference.com/years/' + str(year) + '/scrimmage.htm')
        soup = bs(r.content, 'html.parser')

        parsed_table = soup.find_all('table')[0]
        # print(parsed_table)

        for row in parsed_table.find_all('tr')[2:31]:
            dat = row.find('td', attrs={'data-stat': 'player'})
            name = dat.a.get_text()
            stub = dat.a.get('href')
            # there must be a better way to do this...
            yds = row.find('td', attrs={'data-stat': "yds_from_scrimmage"})
            ydsoup = bs(str(yds), 'html.parser')
            y = ydsoup.td.extract()
            ydsfromscrimage = int(y.string.extract())
            index = index + 1
            allplayers.append([name, stub, ydsfromscrimage])

        start = 32
        notDone = True
        while notDone:

            for row in parsed_table.find_all('tr')[start:(start + 30)]:
                dat = row.find('td', attrs={'data-stat': 'player'})
                name = dat.a.get_text()
                stub = dat.a.get('href')

                yds = row.find('td', attrs={'data-stat': "yds_from_scrimmage"})
                ydsoup = bs(str(yds), 'html.parser')
                y = ydsoup.td.extract()
                ydsfromscrimage = int(y.string.extract())
                index = index + 1
                allplayers.append([name, stub, ydsfromscrimage])
                if ydsfromscrimage <= self.min_total_yards:
                    notDone = False
                    break

            start = start + 31

        return allplayers

    def getPlayerStatTables(self, address):
        playerPage = requests.get('https://www.pro-football-reference.com' + str(address))
        contents = str(playerPage.content).replace("<!--", " ")
        contents = contents.replace("-->", " ")
        soup = bs(contents, 'html.parser')
        tables = soup.find_all('table')
        print(tables)
        return 0


    def getpid(self):
        return hash(self.pname)
