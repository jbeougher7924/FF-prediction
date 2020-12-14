import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# quick link website
# https://www.pro-football-reference.com/years/2012/fantasy.htm

class get_player_data():
    def __init__(self, url='https://www.pro-football-reference.com', year=2013, maxPlayers=10):
        self.url = url
        self.year = year
        self.maxPlayers = maxPlayers
        self.df = []

    # save data passed to it into the file data.html
    def save_to_html(self, data):
        f = open("data.html", "w", encoding='utf-8')
        f.write(str(data))
        f.close()

    def load_from_file(self, fileName):
        url = fileName
        page = open(url)
        return BeautifulSoup(page.read(), features="lxml")

    def load_new_data(self):
        # grab fantasy players
        print("Requesting data from site")
        r = requests.get(self.url + '/years/' + str(self.year) + '/fantasy.htm')
        print("BeautifulSoup working on html.parser")
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup

    def load_test_data(self):
        return self.load_from_file("data.html")

    def get_data(self):
        # uncomment and comment if you want to use new data or test data
        # soup = self.load_new_data()
        soup = self.load_test_data()

        print("Parsing table of data")
        parsed_table = soup.find_all('table')[0]

        # Attempted to count the number of player if maxp exceeded actual number of players
        # row_count = sum(1 for i, row in (parsed_table.find_all('tr')[2:]))
        # print("row count: {}".format(row_count))
        # ******************************************

        # first 2 rows are col headers
        print("Data Access Started")
        for i, row in enumerate(parsed_table.find_all('tr')[2:]):
            i = i + 1
            if i % 10 == 0:
                # print(i, end=' ')
                print("\nCompleted {} of {}".format(i, self.maxPlayers))

            if i > self.maxPlayers:
                print('\nComplete.')
                break

            try:
                dat = row.find('td', attrs={'data-stat': 'player'})
                name = dat.a.get_text()
                stub = dat.a.get('href')
                stub = stub[:-4] + '/fantasy/' + str(self.year)
                pos = row.find('td', attrs={'data-stat': 'fantasy_pos'}).get_text()

                # grab this players stats
                tdf = pd.read_html(self.url + stub)[0]

                # get rid of MultiIndex, just keep last row
                tdf.columns = tdf.columns.get_level_values(-1)

                # fix the away/home column
                tdf = tdf.rename(columns={'Unnamed: 4_level_2': 'Away'})
                tdf['Away'] = [1 if r == '@' else 0 for r in tdf['Away']]

                # print tdf
                # print(tdf)

                # drop all intermediate stats
                tdf = tdf.iloc[:, [1, 2, 3, 4, 5, -3]]

                # drop "Total" row
                tdf = tdf.query('Date != "Total"')

                # add other info

                tdf['Name'] = name
                tdf['Position'] = pos
                tdf['Season'] = self.year

                # Print the TDF to the console for debuging
                # print("TDF")
                # print(tdf)
                # *******************************************

                self.df.append(tdf)

            except Exception as e:
                print("player record {}".format(i-1))
                print("Error {}".format(e))
        # concat the current player rows in the the final data base
        self.df = pd.concat(self.df)
        self.df.head()
        # create a csv file and place the data in the file.  Name the file fantasy"year".csv
        self.df.to_csv("fantasy{}.csv".format(self.year))