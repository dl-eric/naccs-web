import requests
import json
from bs4 import BeautifulSoup as soup

class Matches:
    def __init__(self, headers):
        self.matches_url = 'https://play.esea.net/index.php?s=clubs&d=matches&club_id=70'
        self.headers = headers

    # Parses a soup object for a team name, given 'home' or 'away' status
    def _get_team_name(self, match, name):
        # We expect 'name' to be 'home' or 'away'
        team = match.find('td', attrs={'class': name})
        team_name = team.find(attrs={'class': 'account-insider'})

        if (not team_name):
            team_name = team.find(attrs={'class': 'account-premium'})
        if (not team_name):
            team_name = team.find(attrs={'class': 'account-standard'})

        return team_name.text

    # Gets the first 10 matches (10 because that's how many the websites shows)
    def get_matches(self):
        response = requests.get(self.matches_url, headers=self.headers)
        page_soup = soup(response.text, "html.parser")
        page_soup = page_soup.find("tbody")

        matches = page_soup.find_all("tr")

        json_format = {}

        json_matches = []
        for match in matches:
            json_match = {}

            # Find home team
            home_team_name = self._get_team_name(match, 'home')
            json_match['home'] = home_team_name

            # Find away team
            away_team_name = self._get_team_name(match, 'away')
            json_match['away'] = away_team_name
            
            json_match['score'] = match.find('td', attrs={'class': 'score'}).text
            json_match['home_score'] = json_match['score'].split('-')[0]
            json_match['away_score'] = json_match['score'].split('-')[1]
            json_match['date']  = match.find('td', attrs={'class': 'date'}).text
            json_match['map']   = match.find('td', attrs={'class': 'map'}).text

            json_matches.append(json_match)

        json_format['matches'] = json_matches
        return json_format

if __name__ == "__main__":
    m = Matches()
    print(m.get_matches())
