import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

titles = []
years = []
age_ratings = []
genres = []
directors = []
stars = []
time = []
imdb_ratings = []
metascores = []
votes = []
us_gross = []

headers = {'Accept-Language': 'en-US, en;q=0.5'}
url = 'https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv'

for i in range(20):
    if i == 0:
        url = 'https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv'
    else:
        url = F'https://www.imdb.com/search/title/?groups=top_1000&start={i*50+1}&ref_=adv_nxt'

    results = requests.get(url, headers=headers)
    soup = BeautifulSoup(results.text, 'html.parser')
    movie_div = soup.find_all('div', class_='lister-item mode-advanced')

    for div in enumerate(movie_div):

        titles.append(div[1].h3.a.text)
        years.append(div[1].h3.find('span', class_='lister-item-year').text)
        time.append(div[1].find('span', class_='runtime').text if div[1].find('span', class_='runtime') else '')
        imdb_ratings.append(div[1].strong.text if div[1].strong else '')
        metascores.append(int(div[1].find('span', class_='metascore').text) if div[1].find('span', class_='metascore') else '')
        
        votesGrosses = div[1].find('p', class_='sort-num_votes-visible').find_all('span', attrs={'name': 'nv'})
        votes.append(votesGrosses[0].text)
        us_gross.append(votesGrosses[1].text if len(votesGrosses) > 1 else '')

        age_ratings.append(div[1].p.span.text)
        genres.append(div[1].p.find('span', class_='genre').text)

        directors.append(div[1].find_all('p')[2].a.text)
        names = div[1].find_all('p')[2].find_all('a')
        starNames = ','.join([a[1].text for a in enumerate(names) if a[0] != 0])
        stars.append(starNames)

movies = pd.DataFrame({
    'movie': titles,
    'year': years,
    'age_rating': age_ratings,
    'genre': genres,
    'director': directors,
    'stars': stars,
    'timeMin': time,
    'imdb': imdb_ratings,
    'metascore': metascores,
    'votes': votes,
    'us_grossMillions': us_gross
})

movies['year'] = movies['year'].str.extract('(\d+)').astype(int)
movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int)
movies['metascore'] = movies['metascore'].astype(int, errors='ignore')
movies['votes'] = movies['votes'].str.replace(',', '').astype(int)

movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')

movies['genre'] = movies['genre'].map(lambda x: x.strip())

movies.to_csv('movies.csv')