from python_console_menu import AbstractMenu, MenuItem
from data_scraping import GetPlayerData as gpd
from data_base import DataBaseManager as dbm


class PlayerDataSubMenu(AbstractMenu):
    def __init__(self):
        super().__init__("Player Data Menu.")
        self.year = 0
        self.num_players = 0
        self.savedata = False
        self.players = None

    def initialise(self):
        self.add_menu_item(MenuItem(0, "Exit current menu").set_as_exit_option())
        self.add_menu_item(MenuItem(1, "Load Test Data", lambda: self.load_test_data()))
        self.add_menu_item(MenuItem(2, "Load New Data", lambda: self.load_new_data()))
        self.add_menu_item(MenuItem(3, "Save to  Database", lambda: self.save_to_database()))

    def load_test_data(self):
        self.players = gpd(maxPlayers=1)
        self.players.get_data()
        self.savedata = True

    def load_new_data(self):
        self.year = int(input("Enter Year: "))
        self.num_players = int(input("Enter number of Players to retrieve: "))
        try:
            self.players = gpd(year=self.year, maxPlayers=self.num_players)
            self.players.get_data(False)
            self.savedata = True
        except Exception as e:
            print("Error {}".format(e))
        self.display()
    def save_to_database(self):
        if not self.savedata:
            print("Error no data to save. Program needs to load data before saving.")
            return
        else:
            DB = dbm(df=self.players.get_data_frame())
            DB.create_player_database()


class FFPMenu(AbstractMenu):
    show_hidden_menu = False

    def __init__(self):
        super().__init__("Fantasy Football Prediction.")

    def initialise(self):
        self.add_menu_item(MenuItem(0, "Exit menu").set_as_exit_option())
        self.add_menu_item(MenuItem(1, "Get Player Data ", menu=PlayerDataSubMenu()))
        # self.add_menu_item(MenuItem(2, "Show hidden menu item", lambda: self.__should_show_hidden_menu__()))
        # self.add_hidden_menu_item(MenuItem(3, "Hidden menu item", lambda: print("I was a hidden menu item")))

    # def __should_show_hidden_menu__(self):
    #     print("Showing hidden menu item")
    #     self.show_hidden_menu = True
    #
    # def update_menu_items(self):
    #     if self.show_hidden_menu:
    #         self.show_menu_item(3)

    def item_text(self, item: 'MenuItem'):
        return "%30s" % item.description

    def item_line(self, index: int, item: 'MenuItem'):
        return "%d: %s" % (index, self.item_text(item))


def init_Menu():
    ffp_menu = FFPMenu()
    ffp_menu.display()
