import sqlite3
from pandas import DataFrame


class DataBaseManager:

    def __init__(self, df=None, dn='data/PlayerData.db'):
        self.df = df
        self.dn = dn
        # connect to the PlayerData.db database
        self.conn = sqlite3.connect(dn)

    def createDB(self):
        c = self.conn.cursor()

        c.execute('''CREATE TABLE "Fantasy" (
      "ftid"	INTEGER,
      "year"	INTEGER,
      "age"	INTEGER,
      "G"	INTEGER,
      "FantPos"	INTEGER,
      "FantPt"	INTEGER,
      "VBD"	INTEGER,
      "PosRank"	INTEGER,
      "OvRank"	INTEGER,
      PRIMARY KEY("ftid")
      );''')

        c.execute('''CREATE TABLE "Rushing_Receiving" (
        "ruretid"	INTEGER,
        "year"		INTEGER,
        "age"		INTEGER,
        "TmID"		INTEGER,
        "Pos"		VARCHAR(2),
        "No."	INTEGER,
        "G"		INTEGER,
        "GS"		INTEGER,
        "Rush"		INTEGER,
        "RUSHYds"	INTEGER,
        "RUSHTD"	INTEGER,
        "RUSH1D"	INTEGER,
        "RUSHLng"	INTEGER,
        "RushY/A"	Real,
        "RUSHY/G"	Real,
        "RUSHA/G"	Real,
        "TGT"		INTEGER,
        "Rec"		INTEGER,
        "RECYds"	INTEGER,
        "Y/Rec"		REAL,
        "RECTD"		INTEGER,
        "REC1D"		INTEGER,
        "RECLng"	INTEGER,
        "Rec/G"		REAL,
        "RECY/G"	REAL,
        "CtchPct"		REAL,        
        "Y/Tgt"		REAL,
        "Touch"         INTEGER,
        "Y/Tch"         REAL,
        "YScm"          INTEGER,
        "RRTD"          INTEGER,
        "FMB"           INTEGER,
        "AV"            INTEGER,
        PRIMARY KEY("ruretid")
        );''')

        c.execute('''CREATE TABLE "Player" (
            "pid"        INTEGER,
            "name"       VARCHAR(20), 
            "Year"       INTEGER,
            "Pos"        VARCHAR(2),
            "Ht"         INTEGER,
            "Wt"         INTEGER,
            "40yd"       REAL,
            "Bench"      INTEGER,
            "Broad Jump" REAL,
            "Shuttle"    REAL,
            "3Cone"      REAL,
            "Vertical"   REAL,
            PRIMARY KEY("pid")
            );''')
        c.execute('''CREATE TABLE "Passing" (
            "ptid"       INTEGER,
            "Year"       INTEGER,
            "Age"        INTEGER,
            "TmID"        INTEGER,
            "Pos"        VARCHAR(2),
            "No."        INTEGER,
            "G"          INTEGER,
            "GS"         INTEGER,
            "QBrec"      VARCHAR(20),
            "Cmp"        INTEGER,
            "Att"        INTEGER,
            "Cmp%"       REAL,
            "Yds"        INTEGER,
            "TD"         INTEGER,
            "TD%"        REAL,
            "Int"        INTEGER,
            "Int%"       REAL,
            "1D"         INTEGER,
            "Lng"        INTEGER,
            "Y/A"        REAL,
            "AY/A"       REAL,
            "Y/C"        REAL,
            "Y/G"        REAL,
            "Rate"       REAL,
            "QBR"        REAL,
            "Sk"         INTEGER,
            "SkYdsLost"  INTEGER,
            "NY/A"       REAL,
            "ANY/A"      REAL,
            "Sk%"        REAL,
            "4QC"        INTEGER,
            "GWD"        INTEGER,
            "AV"         INTEGER,
            PRIMARY KEY("ptid")
          );''')
        c.execute('''CREATE TABLE "Adjusted Passing" (
          "aptid"      INTEGER,
          "Year"       INTEGER,
          "Age"        INTEGER,
          "TmID"        INTEGER,
          "Pos"        VARCHAR(2),
          "No."        INTEGER,
          "G"          INTEGER,
          "GS"         INTEGER,
          "QBrec"      VARCHAR(20),	
          "Att"        INTEGER,
          "Y/A+"       REAL,
          "NY/A+"      REAL,
          "AY/A+"      REAL,
          "ANY/A+"     REAL,
          "Cmp%+"      REAL,
          "TD%+"       REAL,
          "Int%+"      REAL,
          "Sack%+"     REAL,
          "Rate+"      REAL,
          PRIMARY KEY("aptid")
          );''')

        c.execute('''CREATE TABLE "Combined" (
          "pid"        INTEGER,
          "ttid"        INTEGER,  
          "year"       INTEGER,
          "ptid"       INTEGER,
          "aptid"      INTEGER,
          "ruretid"    INTEGER,
          "ftid"       INTEGER,  
          FOREIGN KEY("pid") REFERENCES COMBINE("PID"),
          FOREIGN KEY("ttid") REFERENCES TEAM("TTID")
          FOREIGN KEY("ptid") REFERENCES PASSING("PTID"),
          FOREIGN KEY("aptid") REFERENCES ADJ_PASSING("APTID"),
          FOREIGN KEY("ruretid") REFERENCES RUSHING_AND_RECEIVING("RURETID"),
          FOREIGN KEY("ftid") REFERENCES FANTASY("FTID")
        );''')

        c.execute('''CREATE TABLE "Team Stats" (
          "ttid"        INTEGER,
          "TmID"         INTEGER,
          "year"        INTEGER,
          "Player"      VARCHAR(20),
          "PF"          INTEGER,
          "Yds"         INTEGER,
          "Ply"         INTEGER,
          "Y/P"         REAL,
          "TO"          INTEGER,
          "FL"          INTEGER,
          "Tot1stD"    INTEGER,
          "Cmp"         INTEGER,
          "PASSAtt"     INTEGER,
          "PASSYds"     INTEGER,
          "PASSTD"      INTEGER,
          "Int"         INTEGER,
          "NY/A"        REAL,
          "Pass1stD"    INTEGER,
          "RUSHAtt"     INTEGER,
          "RUSHYds"     INTEGER,
          "RUSHTD"      INTEGER,   
          "RUSHY/A"     REAL,
          "RUSH1stD"    INTEGER,
          "Pen"         INTEGER,
          "PENYds"      INTEGER,
          "1stPy"       INTEGER,
          "#Dr"         INTEGER,
          "Sc%"         REAL,
          "TO%"         REAL,
          "Start"       REAL,
          "Time"        TIME,
          "Plays"       REAL,
          "AVGYds"      REAL,
          "AVGPts"      REAL,
          PRIMARY KEY("ttid")
          );''')
        # Save (commit) the changes
        self.conn.commit()
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.conn.close()

    def addtable(self, tabletoinsert, name):
        self.conn = sqlite3.connect(self.dn)
        c = self.conn.cursor()
        df = tabletoinsert
        df.to_sql(name, self.conn, if_exists='replace', index=False)
        # Save (commit) the changes
        self.conn.commit()
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.conn.close()

    def select_all_task(self, table_name, column_name='*'):
        cur = self.conn.cursor()

        command = "SELECT " + column_name + " FROM " + table_name
        cur.execute(command)

        rows = cur.fetchall()

        for row in rows:
            print(row)

        self.conn.close()

