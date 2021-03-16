"""A container module for Title class."""

import requests
from bs4 import BeautifulSoup

class Title:
    """A class for IMDb title.
    """
    def __init__(self, tt, title=None, year=None, rating=None, votes=None):
        """Initilize an object for IMDb title

        Args:
            tt (str): The IMDb id for the title, for example "tt0099685" for Goodfellas
            title (str, optional): The title if known. Defaults to None.
            year (int, optional): Year of the release if known. Defaults to None.
            rating (float, optional): IMDb rating if known. Defaults to None.
            votes (int, optional): Number of votes of known. Defaults to None.
        """
        # Public attributes
        self.imdb_id = tt

        self.title = title
        self.year = year
        self.rating = rating
        self.votes = votes
        self.rating_table = None

        # Private attributes
        self.__soup = None
        self.__rating_soup = None

    def get_id(self):
        return self.imdb_id

    def get_title(self, forced=False):
        """Get the title.

        Args:
            forced (bool, optional): If True, don't use the cached value. Defaults to False.

        Returns:
            [str]: The title
        """
        if self.title and not forced:
            return self.title
        soup = self.__get_soup()
        h1_strings = list(soup.find('div', class_='title_wrapper').h1.strings)
        self.title, self.year = h1_strings[0].strip(), int(
            h1_strings[2].strip())
        return self.title

    def get_year(self, forced=False):
        """Get release year.
        Args:
            forced (bool, optional): If True, don't use the cached value. Defaults to False.

        Returns:
            [int]: Release year
        """
        if self.year and not forced:
            return self.year
        soup = self.__get_soup()
        h1_strings = list(soup.find('div', class_='title_wrapper').h1.strings)
        self.title, self.year = h1_strings[0].strip(), int(
            h1_strings[2].strip())
        return self.year

    def get_rating(self, forced=False):
        """Get IMDb rating

        Args:
            forced (bool, optional): If True, don't use the cached value. Defaults to False.

        Returns:
            [float]: The rating
        """
        if self.rating and not forced:
            return self.rating
        soup = self.__get_soup()
        self.rating = float(
            soup.find('span', {'itemprop': 'ratingValue'}).text.strip())
        return self.rating

    def get_votes(self, forced=False):
        """Get number of votes.

        Args:
            forced (bool, optional): If True, don't use the cached value. Defaults to False.

        Returns:
            [int]: Number of votes
        """
        if self.votes and not forced:
            return self.votes
        soup = self.__get_soup()
        self.votes = int(
            soup.find('span', {'itemprop': 'ratingCount'}).text.strip().replace(',', ''))
        return self.votes

    def get_rating_table(self, forced=False):
        """Get detailed data about rating. Sim

        Args:
            forced (bool, optional): If True, don't use the cached value. Defaults to False.

        Returns:
            [dict]:
                The dictinary has 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 attributes for respective
                general rating and an 'by_sex_age' attribute with the following table:
                                All Ages    ||   <18    ||  18-29   ||  30-44   ||  45+
                    All     ||  [n, r]      ||  [n, r]  ||  [n, r]  ||  [n, r]  ||  [n, r]
                    Males   ||  [n, r]      ||  [n, r]  ||  [n, r]  ||  [n, r]  ||  [n, r]
                    Females ||  [n, r]      ||  [n, r]  ||  [n, r]  ||  [n, r]  ||  [n, r]
        Note:
            See https://www.imdb.com/title/tt0099685/ratings/ for an example.
        """
        if self.rating_table and not forced:
            return self.rating_table
        self.rating_table = {}
        soup = self.__get_rating_soup()
        first_table, second_table, _ = soup.find_all('table')
        for index, td in enumerate(reversed(first_table.findAll('td'))):
            if index % 3 == 0:
                self.rating_table[int(
                    index / 3 + 1)] = int(td.get_text().strip().replace(',', ''))
        self.rating_table['by_sex_age'] = []
        for index, tr in enumerate(second_table.findAll('tr')):
            row = []
            for td in tr.findAll('td'):
                if td.find('div', class_='bigcell') and td.find('div', class_='smallcell'):
                    rating = float(
                        td.find('div', class_='bigcell').text.strip())
                    votes = int(
                        td.find('div', class_='smallcell').text.strip().replace(',', ''))
                    row.append([rating, votes])
            if row:
                self.rating_table['by_sex_age'].append(row)
        return self.rating_table

    def get_rating_by_age(self, forced=False):
        '''
            [all ages, <18, 18-29, 30-44, 45+]
        '''
        return self.get_rating_table(forced=forced)['by_sex_age'][0]

    def get_rating_by_male(self, forced=False):
        '''
            [all ages, <18, 18-29, 30-44, 45+]
        '''
        return self.get_rating_table(forced=forced)['by_sex_age'][1]

    def get_rating_by_female(self, forced=False):
        '''
            [all ages, <18, 18-29, 30-44, 45+]
        '''
        return self.get_rating_table(forced=forced)['by_sex_age'][2]

    def get_rating_by_sex(self, forced=False):
        '''
            [all, male, female]
        '''
        return list(map(lambda x: x[0], self.get_rating_table(forced=forced)['by_sex_age']))

    def get_rating_18(self, forced=False):
        '''
            [all, male, female]
        '''
        return list(map(lambda x: x[1], self.get_rating_table(forced=forced)['by_sex_age']))

    def get_rating_18_29(self, forced=False):
        '''
            [all, male, female]
        '''
        return list(map(lambda x: x[2], self.get_rating_table(forced=forced)['by_sex_age']))

    def get_rating_30_44(self, forced=False):
        '''
            [all, male, female]
        '''
        return list(map(lambda x: x[3], self.get_rating_table(forced=forced)['by_sex_age']))

    def get_rating_45(self, forced=False):
        '''
            [all, male, female]
        '''
        return list(map(lambda x: x[4], self.get_rating_table(forced=forced)['by_sex_age']))

    # Private methods
    def __get_soup(self):
        if self.__soup:
            return self.__soup
        request = requests.get(f'https://www.imdb.com/title/{self.imdb_id}')
        self.__soup = BeautifulSoup(request.content, 'html.parser')
        return self.__soup

    def __get_rating_soup(self):
        if self.__rating_soup:
            return self.__rating_soup
        request = requests.get(f'https://www.imdb.com/title/{self.imdb_id}/ratings')
        self.__rating_soup = BeautifulSoup(request.content, 'html.parser')
        return self.__rating_soup

    def __repr__(self):
        if self.title:
            return f'Id: {self.imdb_id}, title: "{self.title} ({self.year})"'
        return f'Id: {self.imdb_id}'
        