'''
    A module contaning classes to generate titles or names
'''

import re
from typing import Union
import requests
from bs4 import BeautifulSoup
from .__title import Title


class TitleGenerators:
    '''
        A contaner class for title generating methods
    '''
    @staticmethod
    def top_250_generator():
        '''
            Get the Top 250 movies of all time.
        '''
        return TitleGenerators.__top_helper('https://www.imdb.com/chart/top/')

    @staticmethod
    def most_popular_generator():
        '''
            Get the most popular movies from IMDb.
        '''
        return TitleGenerators.__top_helper('https://www.imdb.com/chart/moviemeter/')

    @staticmethod
    def generator(title: str = None,
                  year:           Union[list, int] = None,
                  rating:         Union[list, float] = None,
                  votes:          Union[list, int] = None,
                  genres:         Union[list, str] = None,
                  title_data:     Union[list, str] = None,
                  locations:      Union[list, str] = None,
                  certificates:   Union[list, str] = None,
                  color:          Union[list, str] = None,
                  countries:      Union[list, str] = None,
                  keywords:        Union[list, str] = None,
                  languages:      Union[list, str] = None,
                  popularity:     Union[list, int] = None,
                  runtime:        Union[list, int] = None,
                  sound:          Union[list, str] = None,
                  companies:      Union[list, str] = None,
                  adult:          bool = True,
                  total:          int = 100,
                  url:            str = None
                  ):
        """A method to generate titles. Eqivalent to IMDb Advanced Search.

        Args:
            title (str, optional): Title of the movie. Defaults to None.
            year (Union[list, int], optional): Year or range of years when the movie was released.
                Defaults to None.
            rating (Union[list, float], optional): IMDb rating or range of
                ratings. Defaults to None.
            votes (Union[list, int], optional): Number of votes or range of votes.
                Defaults to None.
            genres (Union[list, str], optional): List of gneres (are combined with AND).
                Defaults to None.
            title_data (Union[list, str], optional): [description]. Defaults to None.
            locations (Union[list, str], optional): [description]. Defaults to None.
            certificates (Union[list, str], optional): [description]. Defaults to None.
            color (Union[list, str], optional): [description]. Defaults to None.
            countries (Union[list, str], optional): [description]. Defaults to None.
            keywords (Union[list, str], optional): [description]. Defaults to None.
            languages (Union[list, str], optional): [description]. Defaults to None.
            popularity (Union[list, int], optional): [description]. Defaults to None.
            runtime (Union[list, int], optional): [description]. Defaults to None.
            sound (Union[list, str], optional): [description]. Defaults to None.
            companies (Union[list, str], optional): [description]. Defaults to None.
            adult (bool, optional): If True, includes Adult movies too. Defaults to True.
            total (int, optional): Maximum number of titles. Defaults to 100.
            url (str, optional): A URL to fetch if configuratins are done with IMDb interface.
                Defaults to None.

        Returns:
            [None]: If there are no titles.

        Yields:
            [generator]: generator of basic_imdb.Title type.
        """
        def list_to_param(lst):
            if not lst:
                return None
            if not isinstance(lst, list):
                lst = [lst]
            if len(lst) < 2:
                return ','.join([str(i) for i in lst]) + ','
            return ','.join([str(i) for i in lst])

        if url:
            request = requests.get(url)
        else:
            request = requests.get('https://www.imdb.com/search/title/', {
                'title': title,
                'title_type': 'feature',
                'release_date': list_to_param(year),
                'user_rating': list_to_param(rating),
                'num_votes': list_to_param(votes),
                'genres': list_to_param(genres),
                'groups': list_to_param(genres),
                'has': list_to_param(title_data),
                'locations': list_to_param(locations),
                'certificates': list_to_param(certificates),
                'colors': list_to_param(color),
                'countries': list_to_param(countries),
                'keywords': list_to_param(keywords),
                'languages': list_to_param(languages),
                'moviemeter': list_to_param(popularity),
                'runtime': list_to_param(runtime),
                'sound_mixes': list_to_param(sound),
                'companies': list_to_param(companies),
                'adult': 'include' if adult else None
            })
        soup = BeautifulSoup(request.content, 'html.parser')
        items = soup.findAll('div', class_='lister-item-content')
        for item in items:
            _title = item.h3.a.text
            year = int(re.sub(r'\D', '', item.find(
                'span', class_='lister-item-year').text))
            if total > 0:
                total -= 1
                yield Title(item.h3.a['href'].replace('/title/', '').replace('/', ''),
                            title=_title.strip(), year=year)
        if total > 0:
            next_link = soup.find('a', class_='lister-page-next next-page')
            if next_link:
                yield from TitleGenerators.generator(url='https://www.imdb.com' + next_link['href'],
                                                    total=total)

    @staticmethod
    def __top_helper(url):
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')
        tds = soup.findAll('td', class_='titleColumn')
        for title_column in tds:
            link = title_column.find('a', href=True)
            year = int(re.sub(r'\D', '', title_column.find(
                'span', class_='secondaryInfo').text))
            yield Title(re.sub(r'\/title\/(tt\d+)\/', r'\1', link['href']),
                        title=link.text.strip(), year=year)
