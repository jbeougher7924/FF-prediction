import requests
from bs4 import BeautifulSoup as bs
import re

#Important constants
min_starts = 5
min_completions = 13
year_start = 2010
year_end = 2020

wanted_tables = ['Passing Table', 'Adjusted Passing Table', 'Rushing &amp; Receiving Table']
errorList = dict()


# Problems
#2016 Terrell Pryor

def pullQB():
    """Gets stats for all qb's between year_start and year_end"""
    # to prevent double pulling, all records that have been pulled will be annotated in here
    pulled = dict()


    # year = 2010

    for year in range(year_start, year_end):
        print('             ', year, '\n')
        qbs = getQuarterbackList(year)

        for entry in qbs:
            name = str(entry[0])
            if not pulled.keys().__contains__(name):
                print('Processing:',name)
                pulled[name] = dict()
                address = str(entry[1])

                playerTables = getPlayerStatTables(address)

                for table in playerTables:
                    table_name = re.findall('<caption>([0-9a-zA-Z &;]+)<', str(table))
                    if len(table_name) > 0 and wanted_tables.__contains__(table_name[0]):
                        #print('table',table)

                        labels = re.findall('scope="col">([a-zA-Z0-9 /%\.\+]+)<', str(table))
                        #print('labels',labels)
                        table_name = table_name[0]

                        print(table_name, '...')
                        pulled[name][table_name] = []
                        pulled[name][table_name].append(labels)
                        pulled[name][table_name].append(processTable(table, table_name))
#------------------->
    return pulled



def getQuarterbackList(year):
    """takes a year as input, returns a list of QBS that
    completed more that min_passes
    returns [last,first, href addres, games started]
    """
    r = requests.get('https://pro-football-reference.com/years/' + str(year) + '/passing.htm')
    soup = bs(r.content, 'html.parser')


    yearsTable = soup.find_all('table')
    if len(yearsTable) > 1:
       yearsTable = yearsTable[1]


    a = re.findall('<tr>(.*)</tr>', str(yearsTable))
    qbs = []

    for line in a:
        try:
            player = []
            name = re.findall('csk="([a-zA-Z\-.]+,[a-zA-Z]+)"', line)
            addr = re.findall('href="/players(/[A-Z]/[a-zA-Z0-9]+)', line)
            gs = re.findall('gs">([0-9]+)<', line)
            ##CHANGE IN FINAL TO <
            if int(gs[0]) < min_starts:
                continue
            cmp = int(re.findall('"pass_cmp">([0-9]+)<', line)[0])  # controls for punters/wr/etc
            if cmp < min_completions:
                continue
            if len(name) == 0:
                continue
            player.append(name[0])
            player.append(addr[0])
            player.append(gs[0])
            qbs.append(player)
        except:
            errorList[name] = year

    return qbs


def getPlayerStatTables(address):
    """Takes the address for the player page
    returns all the stat tables listed on that page"""
    playerPage = requests.get('https://pro-football-reference.com/players' + address + '.htm')
    contents = str(playerPage.content).replace("<!--", " ")
    contents = contents.replace("-->", " ")
    soup = bs(contents, 'html.parser')

    tables = soup.find_all('table')

    return tables


def processTable(table, Tname):
    """takes a table as input, returns a list of all data
    in that table"""
    if Tname == 'Passing Table':
        return processPassingTable(table)
    elif Tname == 'Adjusted Passing Table':
        return processesAdjustedPassingTable(table)
    elif Tname.startswith('Rushing'):
        return processRandR(table)



def processPassingTable(table):
    total_stats = []
    bod = bs(str(table), 'html.parser')
    x = bod.find_all('tbody')
    yearlyStats = re.findall('<tr (.*?)</tr>', str(x))
    for crow in yearlyStats:
        currentStats = []
        crow = str(crow)
        #print(crow)

        # Verify year is within limits
        currentYear = re.findall('years/[0-9]+/">([0-9]+)<', crow)
        if len(currentYear) == 0:
            continue
        currentYear = int(currentYear[0])
        if currentYear < 2010 or currentYear > 2019:
            continue
        print(currentYear)
        currentStats.append(currentYear)

        # Verify games started is within limits
        GS = re.findall('"gs">([0-9]+)<', crow)
        if len(GS) == 0:
            continue
        GS = int(GS[0])
        if GS < min_starts:
            continue

        currentStats.append(int(re.findall('"age">([0-9]+)<', crow)[0]))
        team = re.findall('/teams/([a-z0-9]+)/', crow)
        if len(team) == 0:
            continue
        elif team[0] == '2TM' or team[0] == '3TM':
            continue
        currentStats.append(str(re.findall('/teams/([a-z0-9]+)/', crow)[0]))
        pos = re.findall('"pos">([a-zA-Z]+)<', crow)
        if len(pos) < 1 or str(pos[0]).lower() != 'qb':
            continue
        currentStats.append('qb')
        number = re.findall('"uniform_number">([0-9]+)<', crow)
        if len(number) == 0:
            number = -1
        else:
            number = number[0]
        currentStats.append(int(number))
        currentStats.append(int(re.findall('"g">([0-9]+)<', crow)[0]))
        currentStats.append(GS)
        currentStats.append(str(re.findall('"qb_rec">([0-9]+-[0-9]+-[0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_cmp">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_att">.*?([0-9]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_cmp_perc">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_yds">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_td">.*?([0-9]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_td_perc">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_int">.*?([0-9]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_int_perc">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_first_down">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_long">.*?([0-9]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_yds_per_att">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_adj_yds_per_att">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_yds_per_cmp">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_yds_per_g">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_rating">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"qbr">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_sacked">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_sacked_yds">.*?([0-9]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_net_yds_per_att">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_adj_net_yds_per_att">.*?(-*[0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"pass_sacked_perc">.*?([0-9\.]+)<', crow)[0]))
        frthQC = re.findall('"comebacks">.*?([0-9]*)<', crow)[0]
        if len(frthQC) == 0:
            frthQC = 0
        currentStats.append(int(frthQC))
        GWD = re.findall('"gwd">.*?([0-9]*)<', crow)[0]
        if len(GWD) == 0:
            GWD = 0
        currentStats.append(int(GWD))
        # approximate value.. this could interesting
        currentStats.append(int(re.findall('"av">.*?([0-9]+)<', crow)[0]))
        total_stats.append(currentStats)
    return total_stats


def processesAdjustedPassingTable(table):
    total_stats = []
    bod = bs(str(table), 'html.parser')
    x = bod.find_all('tbody')
    yearlyStats = re.findall('<tr (.*?)</tr>', str(x))
    for crow in yearlyStats:
        currentStats = []
        crow = str(crow)
        # print(crow)

        # Verify year is within limits
        currentYear = re.findall('years/[0-9]+/">([0-9]+)<', crow)
        if len(currentYear) == 0:
            continue
        currentYear = int(currentYear[0])
        if currentYear < 2010 or currentYear > 2019:
            continue
        print(currentYear)
        currentStats.append(currentYear)

        # Verify games started is within limits
        GS = re.findall('"gs">([0-9]+)<', crow)
        if len(GS) == 0:
            continue
        GS = int(GS[0])
        if GS < min_starts:
            continue

        currentStats.append(int(re.findall('"age">([0-9]+)<', crow)[0]))
        team = re.findall('/teams/([a-z0-9]+)/', crow)
        if len(team) == 0:
            continue
        elif team[0] == '2TM' or team[0] == '3TM':
            continue
        currentStats.append(str(re.findall('/teams/([a-z0-9]+)/', crow)[0]))
        pos = re.findall('"pos">([a-zA-Z]+)<', crow)
        if len(pos) < 1 or str(pos[0]).lower() != 'qb':
            continue
        currentStats.append('qb')
        number = re.findall('"uniform_number">([0-9]+)<', crow)
        if len(number) == 0:
            number = -1
        else:
            number = number[0]
        currentStats.append(int(number))
        currentStats.append(int(re.findall('"g">([0-9]+)<', crow)[0]))
        currentStats.append(GS)
        currentStats.append(str(re.findall('"qb_rec">([0-9]+-[0-9]+-[0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_att">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_yds_per_att_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_net_yds_per_att_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_adj_yds_per_att_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_adj_net_yds_per_att_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_cmp_perc_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_td_perc_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_int_perc_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_sacked_perc_index">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"pass_rating_index">.*?([0-9]+)<', crow)[0]))
        total_stats.append(currentStats)
    return total_stats





def processRandR(table):
    total_stats = []
    bod = bs(str(table), 'html.parser')
    x = bod.find_all('tbody')
    yearlyStats = re.findall('<tr (.*?)</tr>', str(x))
    for crow in yearlyStats:
        currentStats = []
        crow = str(crow)
        # print(crow)

        # Verify year is within limits
        currentYear = re.findall('years/[0-9]+/">([0-9]+)<', crow)
        if len(currentYear) == 0:
            continue
        currentYear = int(currentYear[0])
        if currentYear < 2010 or currentYear > 2019:
            continue
        print(currentYear)
        currentStats.append(currentYear)

        # Verify games started is within limits
        GS = re.findall('"gs">([0-9]+)<', crow)
        if len(GS) == 0:
            continue
        GS = int(GS[0])
        if GS < min_starts:
            continue

        currentStats.append(int(re.findall('"age">([0-9]+)<', crow)[0]))
        team = re.findall('/teams/([a-z0-9]+)/', crow)
        if len(team) == 0:
            continue
        elif team[0] == '2TM' or team[0] == '3TM':
            continue
        currentStats.append(str(re.findall('/teams/([a-z0-9]+)/', crow)[0]))
        currentStats.append('qb')
        number = re.findall('"uniform_number">([0-9]+)<', crow)
        if len(number) == 0:
            number = -1
        else:
            number = number[0]
        currentStats.append(int(number))
        currentStats.append(int(re.findall('"g">([0-9]+)<', crow)[0]))
        currentStats.append(GS)
        currentStats.append(int(re.findall('"rush_att">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"rush_yds">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"rush_td">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"rush_first_down">.*?([0-9]+)<', crow)[0]))
        currentStats.append(int(re.findall('"rush_long">.*?([0-9]+)<', crow)[0]))
        currentStats.append(float(re.findall('"rush_yds_per_att">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"rush_yds_per_g">.*?([0-9\.]+)<', crow)[0]))
        currentStats.append(float(re.findall('"rush_att_per_g">.*?([0-9\.]+)<', crow)[0]))

        total_stats.append(currentStats)

    return total_stats



def processessAdvRandR(table):
    return 0

