# from puller import pull
from data_scraping import get_player_data as gpd
# from tests import tester


# main will be the launch point for the program
# other python files will handle the work needed done
if __name__ == '__main__':
    players = gpd(year=2014, maxPlayers=1)
    players.get_data()
