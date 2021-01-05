import puller
from position_scraper import Scraper as scp
import pandas as pd
# from tests import tester
from menu_manager import init_Menu


def main():
    init_Menu()


# # main will be the launch point for the program
# # other python files will handle the work needed done
if __name__ == '__main__':
    main()


# sc =scp.position_scraper.Scraper()
# sc.getPlayerStatTables('/players/C/CharJa00.htm')
# team_data = scp(year_start=2018, year_end=2019)
# team_data.scrapeTeams()



