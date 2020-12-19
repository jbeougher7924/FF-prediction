import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd


# Problems
# The hash function is random, so every time you run this script you get new table id's..



#Important constants
min_starts = 4
min_completions = 13
year_start = 2010
year_end = 2020

#tables to collect
wanted_tables = ['Name', 'Passing Table', 'Adjusted Passing Table', 'Rushing &amp; Receiving Table', 'Fantasy Table', 'Combine Measurements Table']

#table
Quarterbacks = [['Quarterback Table'], ['qbid', 'Name', 'Year Drafted', 'Pos', 'Ht', 'Wt', '40yd', 'Bench', 'Broad Jump', 'Shuttle', '3Cone', 'Vertical']]
Passing_table = [['Passing Table'], ['ptid', 'qbid',  'Name', 'Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Cmp', 'Att', 'Cmp%', 'Yds', 'TD', 'TD%', 'Int', 'Int%', '1D', 'Lng', 'Y/A', 'AY/A', 'Y/C', 'Y/G', 'Rate', 'QBR', 'Sk', 'Yds', 'NY/A', 'ANY/A', 'Sk%', '4QC', 'GWD', 'AV']]
Adj_Passing_table = [['Adjusted Passing Table'],['aptid', 'qbid', 'Name', 'Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'QBrec', 'Att', 'Y/A+', 'NY/A+', 'AY/A+', 'ANY/A+', 'Cmp%+', 'TD%+', 'Int%+', 'Sack%+', 'Rate+']]
Rush_Rec_table = [['Rush and Receiving Table'], ['arrtid', 'qbid', 'Name', 'Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'Rush', 'Yds', 'TD', '1D', 'Lng', 'Y/A', 'Y/G', 'A/G', 'Tgt', 'Rec', 'Yds', 'Y/R', 'TD', '1D', 'Lng', 'R/G', 'Y/G', 'Ctch%', 'Y/Tgt', 'Touch', 'Y/Tch', 'YScm', 'RRTD', 'Fmb']]
Fantasy_Table = [['Fantasy Table'], ['ftid', 'qbid', 'Name', 'Year', 'Age', 'G', 'FantPos', 'FantPt', 'VBD', 'PosRank', 'OvRank']]
Statistics_Table = [['Statistics Table'], ['qbid', 'year', 'ptid', 'aptid', 'arrtid', 'ftid']]

#caught errors
errorList = []

#This value keeps track of years with the minimum completions and starts
#only fantasy pts from these years will be collected
current_years = []

Pname = ""
qbid = 0

class Puller:

    def __init__(self, minStarts=5, minComps=13, yStart=2010, yEnd=2011):
        self.min_starts = minStarts
        self.min_completions = minComps
        self.year_start = yStart
        self.year_end = yEnd


    def pullQB(self):
        """Gets stats for all qb's between year_start and year_end"""
        # to prevent double pulling, all records that have been pulled will be annotated in here
        pulled = dict()

        for year in range(year_start, year_end):
            print('             ', year, '\n')
            qbs = self.getQuarterbackList(year)

            for entry in qbs:
                Pname = str(entry[0])

                if not pulled.keys().__contains__(Pname):
                    print('Processing:              ', self.processPname(Pname))
                    pulled[Pname] = dict()
                    address = str(entry[1])
                    self.Pname = self.processPname(Pname)
                    self.qbid = hash(self.Pname)
                    playerTables = self.getPlayerStatTables(address)

                    for table in playerTables:
                        table_name = re.findall('<caption>([0-9a-zA-Z &;]+)<', str(table))
                        if len(table_name) > 0 and wanted_tables.__contains__(table_name[0]):

                            labels = re.findall('scope="col">([a-zA-Z0-9 /%\.\+]+)<', str(table))
                            #print('labels',labels)
                            table_name = table_name[0]

                            print(table_name, '...')
                            pulled[Pname][table_name] = []
                            pulled[Pname][table_name].append(labels)
                            pulled[Pname][table_name].append(self.processTable(table, table_name, Pname))


        print('ERRORS', errorList)
        return [Passing_table, Adj_Passing_table, Rush_Rec_table, Fantasy_Table, Quarterbacks]
        #return pulled


    def getQuarterbackList(self, year):
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
                if int(gs[0]) < self.min_starts:
                    continue
                cmp = int(re.findall('"pass_cmp">([0-9]+)<', line)[0])  # controls for punters/wr/etc
                if cmp < self.min_completions:
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


    def getPlayerStatTables(self, address):
        """Takes the address for the player page
        returns all the stat tables listed on that page"""
        playerPage = requests.get('https://pro-football-reference.com/players' + address + '.htm')
        contents = str(playerPage.content).replace("<!--", " ")
        contents = contents.replace("-->", " ")
        soup = bs(contents, 'html.parser')

        tables = soup.find_all('table')

        return tables


    def processTable(self, table, Tname, Pname):
        """takes a table as input, returns a list of all data
        in that table"""
        Pname = self.processPname(Pname)
        if Tname == 'Passing Table':
            return self.processPassingTable(table, Pname)
        elif Tname == 'Adjusted Passing Table':
            return self.processesAdjustedPassingTable(table, Pname)
        elif Tname.startswith('Rushing'):
            return self.processRandR(table, Pname)
        elif Tname == 'Fantasy Table':
            return self.processFantasy(table, Pname)
        elif Tname == 'Combine Measurements Table':
            return self.processCombine(table, Pname)



    def processPassingTable(self, table, Pname):
        total_stats = []
        bod = bs(str(table), 'html.parser')
        x = bod.find_all('tbody')
        yearlyStats = re.findall('<tr (.*?)</tr>', str(x))
        for crow in yearlyStats:
            try:
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
                #print(currentYear)
                currentStats.append(hash(self.processPname(Pname) + str(currentYear)))
                currentStats.append(self.qbid)
                currentStats.append(Pname)
                currentStats.append(currentYear)

                # Verify games started is within limits
                GS = re.findall('"gs">([0-9]+)<', crow)
                if len(GS) == 0:
                    continue
                GS = int(GS[0])
                if GS < self.min_starts:
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
                Passing_table.append(currentStats)
                current_years.append(currentYear)

            except:
                errorList.append([Pname, currentYear, "Passing"])
        return total_stats


    def processesAdjustedPassingTable(self, table, Pname):
        total_stats = []
        bod = bs(str(table), 'html.parser')
        x = bod.find_all('tbody')
        yearlyStats = re.findall('<tr (.*?)</tr>', str(x))
        for crow in yearlyStats:
            try:
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
                #print(currentYear)
                currentStats.append(hash(self.processPname(Pname) + str(currentYear)))
                currentStats.append(self.qbid)
                currentStats.append(Pname)
                currentStats.append(currentYear)

                # Verify games started is within limits
                GS = re.findall('"gs">([0-9]+)<', crow)
                if len(GS) == 0:
                    continue
                GS = int(GS[0])
                if GS < self.min_starts:
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
                Adj_Passing_table.append(currentStats)
            except:
                errorList.append([Pname, currentYear, "Adjusted Passing"])
        return total_stats





    def processRandR(self, table, Pname):
        total_stats = []
        bod = bs(str(table), 'html.parser')
        x = bod.find_all('tbody')
        yearlyStats = re.findall('<tr (.*?)</tr>', str(x))
        for crow in yearlyStats:
            try:
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
                #print(currentYear)
                currentStats.append(hash(self.processPname(Pname) + str(currentYear)))
                currentStats.append(self.qbid)
                currentStats.append(Pname)
                currentStats.append(currentYear)

                # Verify games started is within limits
                GS = re.findall('"gs">([0-9]+)<', crow)
                if len(GS) == 0:
                    continue
                GS = int(GS[0])
                if GS < self.min_starts:
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

                currentStats.append(int(self.checkValue(re.findall('"targets">([0-9]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"rec">([0-9]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"rec_yds">([0-9-]+)<', crow))))
                currentStats.append(float(self.checkValue(re.findall('"rec_yds_per_rec">([0-9\.-]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"rec_td">([0-9]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"rec_first_down">([0-9]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"rec_long">([0-9-]+)<', crow))))
                currentStats.append(float(self.checkValue(re.findall('"rec_per_g">([0-9\.]+)<', crow))))
                currentStats.append(float(self.checkValue(re.findall('"rec_yds_per_g">([0-9\.-]+)<', crow))))
                currentStats.append(float(self.checkValue(re.findall('"catch_pct">([0-9\.]+)<', crow))))
                currentStats.append(float(self.checkValue(re.findall('"rec_yds_per_tgt">([0-9\.]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"touches">([0-9]+)<', crow))))
                currentStats.append(float(self.checkValue(re.findall('"yds_per_touch">([0-9\.-]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"yds_from_scrimmage">([0-9-]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"rush_receive_td">([0-9-]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"fumbles">([0-9-]+)<', crow))))

                total_stats.append(currentStats)
                Rush_Rec_table.append(currentStats)
            except:
                errorList.append([Pname, currentYear, "Rushing and Receiving" ])

        return total_stats

    def processFantasy(self, table, Pname):
        total_stats = []
        bod = bs(str(table), 'html.parser')
        x = bod.find_all('tbody')
        yearlyStats = re.findall('<tr (.*?)</tr>', str(x))

        for row in yearlyStats:
            try:

                currentStats = []
                crow = str(row)
                #print(crow)

                # Verify year is within limits
                currentYear = re.findall('"/years/[0-9]+/fantasy.htm">([0-9]+)<', crow)
                if len(currentYear) == 0:
                    continue
                currentYear = int(currentYear[0])
                if currentYear < 2010 or currentYear > 2019 or currentYear not in current_years:
                    continue
                #print(currentYear)
                currentStats.append(hash(self.processPname(Pname) + str(currentYear)))
                currentStats.append(self.qbid)
                currentStats.append(Pname)
                currentStats.append(currentYear)
                currentStats.append(int(re.findall('"age">([0-9]+)<', crow)[0]))
                currentStats.append(int(re.findall('"g">([0-9]+)<', crow)[0]))
                pos = re.findall('"fantasy_pos">([a-zA-Z]+)<', crow)
                if len(pos) < 1 or str(pos[0]).lower() != 'qb':
                    continue
                currentStats.append('qb')
                currentStats.append(int(self.checkValue(re.findall('"fantasy_points">.*?([0-9-]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"vbd">([0-9-]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"fantasy_rank_pos">.*?([0-9-]+)<', crow))))
                currentStats.append(int(self.checkValue(re.findall('"fantasy_rank_overall">.*?([0-9-]+)<', crow))))

                total_stats.append(currentStats)
                Fantasy_Table.append(currentStats)



            except:
                errorList.append([Pname, currentYear, "Fantasy Pts"])

        current_years.clear()
        return total_stats

    def processCombine(self, table, Pname):
        total_stats = []
        bod = bs(str(table), 'html.parser')
        crow = bod.find_all('tbody')

        try:
            currentStats = []
            currentStats.append(self.qbid)
            currentStats.append(Pname)
            crow = str(crow)
            # Verify year is within limits
            currentYear = re.findall('"/draft/[0-9]+-combine.htm">([0-9]+)<', crow)
            if len(currentYear) == 0:
                errorList.append([Pname, -1, "Combine Score"])
                return []
            else:
                currentYear = int(currentYear[0])
            currentStats.append(currentYear)
            pos = re.findall('"pos">([a-zA-Z]+)<', crow)
            if len(pos) < 1 or str(pos[0]).lower() != 'qb':
                errorList.append([Pname, currentYear, "Combine Score"])
                return []
            currentStats.append('qb')
            currentStats.append(int(self.checkValue2(re.findall('"height">([0-9]+)<', crow))))
            currentStats.append(int(self.checkValue2(re.findall('"weight">([0-9]+)<', crow))))
            currentStats.append(float(self.checkValue2(re.findall('"forty_yd">([0-9\.]+)<', crow))))
            currentStats.append(int(self.checkValue2(re.findall('"bench_reps">([0-9]+)<', crow))))
            currentStats.append(int(self.checkValue2(re.findall('"broad_jump">([0-9]+)<', crow))))
            currentStats.append(float(self.checkValue2(re.findall('"shuttle">([0-9\.]+)<', crow))))
            currentStats.append(float(self.checkValue2(re.findall('"cone">([0-9\.]+)<', crow))))
            currentStats.append(float(self.checkValue2(re.findall('"vertical">([0-9\.]+)<', crow))))
            Quarterbacks.append(currentStats)

        except:
            errorList.append([Pname, currentYear, "Combine Score"])

        return currentStats

    def checkValue(self, val):
        if len(val) == 0:
            return 0
        return val[0]

    def checkValue2(self, val):
        if len(val) == 0:
            return -1
        return val[0]

    def processPname(self, pname):
        return pname.strip().replace(',', ' ')

    def outputAsCSV(self, groupTables):
        for table in groupTables:
            tableName = table[0][0]
            tableData = pd.DataFrame(table[2:], columns=table[1])
            tableData.to_csv("QB {}".format(tableName))


