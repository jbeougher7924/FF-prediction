import requests
from bs4 import BeautifulSoup as bs
import re

# Problems
#   The web pages for current starters have the 'season' table first
#   Other tables are hidden in table wrappers.. how do I access these?

def pull():
    # to prevent double pulling, all records that have been pulled will be annotated in here
    pulled = dict()

    # Get a list of all quarterbacks that played in a given year starting in 2010

    # year = 2010

    for year in range(2018, 2020):
        print('             ', year, '\n')
        r = requests.get('https://pro-football-reference.com/years/' + str(year) + '/passing.htm')
        soup = bs(r.content, 'html.parser')

        pt = soup.find_all('table')[0]

        a = re.findall('<tr>(.*)</tr>', str(pt))
        qbs = []

        for line in a:
            player = []
            name = re.findall('csk="([a-zA-Z\-.]+,[a-zA-Z]+)"', line)
            addr = re.findall('href="/players(/[A-Z]/[a-zA-Z0-9]+)', line)
            gs = re.findall('gs">([0-9]+)<', line)
            cmp = int(re.findall('"pass_cmp">([0-9]+)<', line)[0])  # controls for punters/wr/etc
            if cmp < 13:
                continue
            if len(name) == 0:
                continue
            player.append(name[0])
            player.append(addr[0])
            player.append(gs[0])
            qbs.append(player)

        for entry in qbs:
            name = str(entry[0])
            # change entry[2] > 3
            # and not pulled.keys().contains(entry[0]
            if int(entry[2]) == 5 and not pulled.keys().__contains__(name):

                pulled[name] = dict()

                playerPage = requests.get('https://pro-football-reference.com/players' + str(entry[1]) + '.htm')
                soup = bs(playerPage.content, 'html.parser')

                # iterate over the tables HOW DO I DO THIS?
                playerTables = soup.find_all('table')[0]

                labels = re.findall('<th aria-label="([a-zA-Z0-9 %]+)"', str(playerTables))
                # pulled[name]['passing'] = labels
                pulled[name]['passing'] = []
                pulled[name]['passing'].append(labels)

                # pull all years of stats from curent table and divide them into rows
                yearlyStats = re.findall('<tr (.*)</tr>', str(playerTables))

                # Iterate over the rows and fill the dictionary
                # Check for GS >= 4
                # Filter years <2010 or >2019
                print(name)
                for row in yearlyStats:
                    currentStats = []
                    row = str(row)
                    print(row)

                    # Verify year is within limits
                    currentYear = re.findall('years/[0-9]+/">([0-9]+)<', row)
                    if len(currentYear) == 0:
                        continue
                    currentYear = int(currentYear[0])
                    if currentYear < 2010 or currentYear > 2019:
                        continue
                    print(currentYear)
                    currentStats.append(currentYear)

                    # Verify games started is within limits
                    GS = re.findall('"gs">([0-9]+)<', row)
                    if len(GS) == 0:
                        continue
                    GS = int(GS[0])
                    if GS < 4:
                        continue
                    currentStats.append(GS)

                    currentStats.append(int(re.findall('"age">([0-9]+)<', row)[0]))
                    team = re.findall('/teams/([a-z0-9]+)/', row)
                    if len(team) == 0:
                        continue
                    elif team[0] == '2TM' or team[0] == '3TM':
                        continue
                    currentStats.append(str(re.findall('/teams/([a-z0-9]+)/', row)[0]))
                    currentStats.append('qb')
                    number = re.findall('"uniform_number">([0-9]+)<', row)
                    if len(number) == 0:
                        number = -1
                    else:
                        number = number[0]
                    currentStats.append(int(number))
                    currentStats.append(int(re.findall('"g">([0-9]+)<', row)[0]))
                    currentStats.append(str(re.findall('"qb_rec">([0-9]+-[0-9]+-[0-9]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_cmp">.*([0-9]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_att">.*([0-9]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_cmp_perc">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_yds">.*([0-9]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_td">.*([0-9]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_td_perc">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_int">.*([0-9]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_int_perc">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_first_down">.*([0-9]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_long">.*([0-9]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_yds_per_att">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_adj_yds_per_att">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_yds_per_cmp">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_yds_per_g">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_rating">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(float(re.findall('"qbr">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_sacked">.*([0-9]+)<', row)[0]))
                    currentStats.append(int(re.findall('"pass_sacked_yds">.*([0-9]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_net_yds_per_att">.*([0-9\.]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_adj_net_yds_per_att">.*(-*[0-9\.]+)<', row)[0]))
                    currentStats.append(float(re.findall('"pass_sacked_perc">.*([0-9\.]+)<', row)[0]))
                    frthQC = re.findall('"comebacks">.*([0-9]*)<', row)[0]
                    if len(frthQC) == 0:
                        frthQC = 0
                    currentStats.append(int(frthQC))
                    GWD = re.findall('"gwd">.*([0-9]*)<', row)[0]
                    if len(GWD) == 0:
                        GWD = 0
                    currentStats.append(int(GWD))
                    # approximate value.. this could interesting
                    currentStats.append(int(re.findall('"av">.*([0-9]+)<', row)[0]))
                    pulled[name]['passing'].append(currentStats)
    return pulled



