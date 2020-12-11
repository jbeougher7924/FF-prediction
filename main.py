import requests
from bs4 import BeautifulSoup as bs
import re


url = 'https://www.pro-football-reference.com/years/'
year = 2010

r = requests.get('https://pro-football-reference.com/years/' + str(year) + '/passing.htm')
soup = bs(r.content, 'html.parser')

pt = soup.find_all('table')[0]

a = re.findall('<tr>(.*)</tr>',str(pt))
qbs = []

for line in a:
    player = []
    name = re.findall('csk="([a-zA-Z\-.]+,[a-zA-Z]+)"', line)
    addr = re.findall('href="/players(/[A-Z]/[a-zA-Z0-9]+)', line)
    gs = re.findall('gs">([0-9]+)<', line)
    if len(name) == 0:
        continue
    player.append(name[0])
    player.append(addr[0])
    player.append(gs[0])
    qbs.append(player)

for entry in qbs:
    print(entry)



