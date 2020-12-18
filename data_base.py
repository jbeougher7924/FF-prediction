import sqlite3
from pandas import DataFrame

class DataBaseManager:
    def __init__(self, df=None):
        self.df = df
        # connect to the PlayerData.db database
        self.conn = sqlite3.connect('PlayerData.db')

    def create_player_database(self):
        # init an empty string to hold the column names to be used in the sql statement
        column_names = ""

        #  build the the string based on the names of the columns in the dataframe
        for i, header in enumerate(self.df.columns.values.tolist()):
            header = header.strip('#')
            column_names = column_names + ", {} text".format(header)

        # need to send command to the sql database
        c = self.conn.cursor()
        # string that will be the query statement to be executed on the database using the column name string.
        # Table is created if it does not exists
        qry = 'CREATE TABLE IF NOT EXISTS PLAYERS(id integer PRIMARY KEY {})'.format(column_names)
        # print(qry)
        # run the query statement
        c.execute(qry)
        # commit the changes to the database
        self.conn.commit()
        # transfer the dataframe data to a sql database
        self.df.to_sql('PLAYERS', self.conn, if_exists='replace')





