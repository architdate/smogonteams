import requests
import sys
from bs4 import BeautifulSoup

def grab_links(url, linkbase):
    content = requests.get(url).text
    soup = BeautifulSoup(content,'html.parser')

    pages = [link.a.get('href') for link in soup.find_all('li', class_='pageNav-page') if '/page-' in str(link.a.get('href'))]
    max_page = max([int(p.rsplit('-', 1)[1]) for p in pages])

    pages = [url] + [url.strip('/') + f'/page-{i}' for i in range(2, max_page + 1)]
    teamlinks = []
    teams = []
    for i in pages:
        content = requests.get(i).text
        teamlinks += grab_links_single(i, linkbase, content)
        teams += grab_teams(i, content)
    return (list(set(teams)), list(set(teamlinks)))

def grab_links_single(single, linkbase, content = None):
    if content == None:
        content = requests.get(single).text
    soup = BeautifulSoup(content,'html.parser')
    links = [link.get('href') for link in soup.find_all('a') if link.get('href') is not None]
    valid_links = []
    for l in links:
        for b in linkbase:
            if b in l:
                valid_links.append(l)
    return valid_links

def grab_teams(single, content = None):
    if content == None:
        content = requests.get(single).text
    soup = BeautifulSoup(content, 'html.parser')
    pteams = soup.find_all('div', class_ = 'bbCodeBlock-content')
    pteams_text = [pteam.get_text() for pteam in pteams]
    sanitized = []
    for team in pteams_text:
        if all(x in team for x in ['@', ' Nature', 'Ability: ', '/', '- ']):
            sanitized.append(team)
    filtered_teams = []
    for pteam in sanitized:
        breaker = pteam.rsplit('- ', 1)[1].split('\n')
        if len(breaker) > 1:
            stripped_team = pteam.rsplit('\n' + breaker[1])[0]
        else:
            stripped_team = pteam
        filtered_teams.append(stripped_team.replace('<br />', '\r\n').replace('</div>', ''))
    return [team.strip() for team in filtered_teams if team.strip() != '']

def pretty_print(output):
    teamlinks = output[1]
    teams = output[0]
    if len(teamlinks) > 0:
        print("Links: \n")
        for i in teamlinks:
            print(i)
    print('\n\n')
    if len(teams) > 0:
        print("Teams: \n")
        for i in teams:
            print('====')
            print(i)

if __name__ == "__main__":
    url = 'https://www.smogon.com/forums/threads/swsh-ou-bazaar.3656490/'
    linkbase = ['pokepast.es', 'pastebin.com', 'hastebin.com']
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if 'www.smogon.com/forums' not in url:
            print("Invalid Smogon Forum URL")
        else:
            pretty_print(grab_links(url, linkbase))
    else:
        pretty_print(grab_links(url, linkbase))