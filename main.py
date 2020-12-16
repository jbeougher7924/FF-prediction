# from puller import pull
from data_scraping import GetPlayerData as gpd
from data_base import DataBaseManager as dbm
# from tests import tester


# main will be the launch point for the program
# other python files will handle the work needed done
if __name__ == '__main__':
    players = gpd(year=2014, maxPlayers=30)
    players.get_data()
    DB = dbm(df=players.get_data_frame())
    DB.create_player_database()


