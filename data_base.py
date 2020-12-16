import sqlite3
from pandas import DataFrame

class DataBaseManager:
    def __init__(self, df=None):
        self.df = df
        self.conn = sqlite3.connect('PlayerData.db')

    def create_player_database(self):
        column_names = ""
        for i, header in enumerate(self.df.columns.values.tolist()):
            header = header.strip('#')
            column_names = column_names + ", {} text".format(header)

        c = self.conn.cursor()
        qry = 'CREATE TABLE IF NOT EXISTS PLAYERS(id integer PRIMARY KEY {})'.format(column_names)
        print(qry)
        c.execute(qry)
        self.conn.commit()
        self.df.to_sql('PLAYERS', self.conn, if_exists='replace')





