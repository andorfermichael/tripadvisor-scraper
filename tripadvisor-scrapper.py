import argcomplete
import argparse
import json
import logging
import sys
import urllib2
import time
from functools import wraps
from bs4 import BeautifulSoup

# Define base url of TripAdvisor
BASE_URL = 'http://www.tripadvisor.com/'

# TODO: Load from file or enter via commandline
CITY_DEFAULT_URL = 'Hotels-g293974-Istanbul-Hotels.html'

CITY_URL = BASE_URL + CITY_DEFAULT_URL

# Retrieve url content of city (first page)
content = urllib2.urlopen(CITY_URL)

# Define parser
soup = BeautifulSoup(content, 'html.parser')

# Scrape number of pages (pagination of hotels in the city)
number_of_pages_in_city = soup.find('a', attrs={'class': 'last'}).contents[0]

number_of_cities_per_page = 30
number_of_reviews_per_page = 10

city_pagination_urls = list()
city_hotel_urls = list()

# Get all pagination urls of the city
for i in range(0, 2):#int(number_of_pages_in_city)):
    if i == 0:
        # Append the already available first page url
        city_pagination_urls.append(CITY_DEFAULT_URL)
    else:
        # Calculate the dash positions
        occurences_of_dash = [j for j in range(len(CITY_DEFAULT_URL)) if CITY_DEFAULT_URL.startswith('-', j)]

        # Get the second dash position
        second_dash_index = occurences_of_dash[1]

        # Each page contains 30 hotels
        city_pagination = i * 30

        # Build the current page url and append it to the list
        current_city_pagination_url = CITY_DEFAULT_URL[:second_dash_index] + '-oa' + str(city_pagination) + CITY_DEFAULT_URL[second_dash_index:] + '#ACCOM_OVERVIEW'
        city_pagination_urls.append(current_city_pagination_url)

# Get all hotel urls of the city
for current_city_pagination_url in city_pagination_urls[1:]:
    # Build url out of base and current page url
    CITY_URL = BASE_URL + current_city_pagination_url

    # Retrieve url content of the page url
    content = urllib2.urlopen(CITY_URL)

    # Define parser
    soup = BeautifulSoup(content, 'html.parser')

    # Store each hotel url in the list
    for j, city_hotel_url in enumerate(soup.find_all('a', attrs={'class': 'property_title '})):
        city_hotel_urls.append(soup.find_all('a', attrs={'class': 'property_title '})[j]['href'])

# Visit each hotel url in the city
for city_hotel_url in city_hotel_urls[1:]:
    # Build url out of base and current page url
    HOTEL_URL = BASE_URL + city_hotel_url

    # Retrieve url content of the page url
    content = urllib2.urlopen(HOTEL_URL)

    # Define parser
    soup = BeautifulSoup(content, 'html.parser')

    hotel_pagination_urls = list()

    pagination_items = soup.find_all('a', attrs={'class': 'pageNum'})

    # Scrape the highest pagination value of a hotel's pages
    max = 0
    for page in pagination_items:
        if page.contents[0] > max:
            max = page.contents[0]

    maximum_pagination_of_hotel = int(max)

    # Get all pagination urls of the hotel
    for i in range(0, maximum_pagination_of_hotel):
        if i == 0:
            # Append the already available first page url
            hotel_pagination_urls.append(HOTEL_URL)
        else:
            # Calculate the dash positions
            occurrences_of_dash = [j for j in range(len(HOTEL_URL)) if HOTEL_URL.startswith('-', j)]

            # Get the fourth dash position
            fourth_dash_index = occurrences_of_dash[3]

            # Each page contains 30 hotels
            city_pagination = i * 10

            # Build the current page url and append it to the list
            hotel_page_url = CITY_URL[:fourth_dash_index] + '-or' + str(city_pagination) + HOTEL_URL[fourth_dash_index:] + '#REVIEW'
            hotel_pagination_urls.append(hotel_page_url)


for page in hotel_pagination_urls:
    print(page)


#https://www.tripadvisor.com/Hotel_Review-g293974-d1181320-Reviews-Osmanhan_Hotel-Istanbul.html#REVIEWS
#https://www.tripadvisor.com/Hotel_Review-g293974-d1181320-Reviews-or10-Osmanhan_Hotel-Istanbul.html#REVIEWS

# /Hotels-g293974-oa30-Istanbul-Hotels.html#ACCOM_OVERVIEW

#for i in range(number_of_pages):
#    hotel_links.append(soup.find('a', attrs={'class': 'property_title '})['href'])


#<a class="pageNum taLnk" onclick="ta.hac.filters.paging(this, event); ta.trackEventOnPage('STANDARD_PAGINATION', 'page', '2', 0);" data-offset="30" data-page-number="2" href="/Hotels-g293974-oa30-Istanbul-Hotels.html#ACCOM_OVERVIEW">2</a>

'''<a onclick="ta.hac.filters.paging(this, event); ta.trackEventOnPage('STANDARD_PAGINATION', 'last', '37', 0);" class="pageNum last taLnk" data-offset="1080" data-page-number="37" href="/Hotels-g293974-oa1080-Istanbul-Hotels.html#ACCOM_OVERVIEW">37</a>'''




"""
def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

# Generates a movie json
def gen_json(movies):
    with open('movies.json', mode='w') as moviesjson:
        json.dump(movies, moviesjson)

# Requests the IMDb data for a given movie id
def process_page(url):

    # Retrieve html and setup parser
    @retry(Exception, tries=20, delay=5, backoff=2)
    def urlopen_with_retry():
        return urllib2.urlopen(url)

    soup = BeautifulSoup(urlopen_with_retry(), 'html.parser')

    # Process all table rows
    for tr in soup.find_all('tr'):
        try:
            # Parse single movie information
            id = tr.find('td', attrs={'class': 'title'}).find('a')['href'][8:-1]
            title = tr.find('td', attrs={'class': 'title'}).find('a').contents[0]
            year = tr.find('td', attrs={'class': 'title'}).find('span', attrs={'class': 'year_type'}).string[1:-1]
            outline = tr.find('td', attrs={'class': 'title'}).find('span', attrs={'class': 'outline'}).string
            director = tr.find('td', attrs={'class': 'title'}).find('span', attrs={'class': 'credit'}).find('a').contents[0]
            certificate = tr.find('td', attrs={'class': 'title'}).find('span', attrs={'class': 'certificate'}).find('span')['title']
            runtime = tr.find('td', attrs={'class': 'title'}).find('span', attrs={'class': 'runtime'}).string

            image_url = tr.find('td', attrs={'class': 'image'}).find('a').find('img')['src'][:-27] + '._V1_UX182_CR0, 0, 182, 268AL_.jpg'

            # Parse actors
            actors = list()
            actors_temp = tr.find('td', attrs={'class': 'title'}).find('span', attrs={'class': 'credit'}).find_all('a')
            for i, a in enumerate(actors_temp):
                if i != 0:
                    actors.append(actors_temp[i].contents[0])

            # Parse genres
            genres = list()
            genres_temp = tr.find('td', attrs={'class': 'title'}).find('span', attrs={'class': 'genre'}).find_all('a')
            for i, a in enumerate(genres_temp):
                genres.append(genres_temp[i].contents[0])

            # Store the movie data in a dictionary
            movie = {
                "actor": actors,
                "certification": certificate,
                "director": director,
                "genre": genres,
                "id": id,
                "title": title,
                "outline": outline,
                "image_url": image_url,
                "runtime": runtime,
                "year": year
            }

            # Append the movie data dictionary to the movies dictionary
            movies['movies'].append(movie)

            # Store the update movies dictionary in the json file (after each request)
            if args.storing == 'save':
                gen_json(movies)
                logger.info('Movie with id ' + id + ' stored in "movies.json".')
        except:
            continue

# Removes the wrapping dictionary of the data in the json file
def clean_json():
    # Load the dictionary from json file
    with open('movies.json') as f:
        movies = json.load(f)

    # Get the value of the wrapping dictionary
    movies_temp = movies['movies']

    # Store the unwrapped dictionaries
    with open('movies.json', mode='w') as moviesjson:
        json.dump(movies_temp, moviesjson)

# Main
if __name__ == '__main__':
    # Reload does the trick!
    reload(sys)

    # Set default encoding
    sys.setdefaultencoding('utf-8')

    # Define commandline arguments
    parser = argparse.ArgumentParser(description='scrape feature movies from IMDB''s "Most Voted Feature Films" list' , usage='python imdb-page-scrapper.py 10000 save')
    parser.add_argument('number', type=int, help='number of movies to request')
    parser.add_argument('storing', choices=['save', 'unsave'],
                        help='[save] store movies data after each request,[unsave] store movies data after all requests were executed')
    parser.add_argument('--start', type=int, help='the ranking number to start with')
    parser.add_argument('--overwrite', default='yes', choices=['yes', 'no'], help='[yes] overwrite json file, [no] append json file')
    args = parser.parse_args()

    if args.number < 0 or args.number % 50 != 0:
        parser.error('number has to be 50 or a multiple of 50 (e.g. 100, 250, 1500)')

    if args.start != None and (args.start < 0 or args.start % 50 != 0):
        parser.error('--start has to be 1, 50 or a multiple of 50 (e.g. 100, 250, 1500)')

    argcomplete.autocomplete(parser)

    # Set up a specific logger with desired output level
    logging.basicConfig(filename='./logs/imdb-page-scrapper.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger().addHandler(logging.StreamHandler())

    # Only show warnings for urllib2 library
    logging.getLogger('urllib2').setLevel(logging.WARNING)

    if args.start != None:
        START_ID = args.start
    else:
        START_ID = 0

    MAX_ITERATIONS = args.number

    if args.overwrite == 'yes':
        # Create a clean json file
        logger.info('JSON file "movies.json" created.')
        with open('movies.json', mode='w') as moviesjson:
            json.dump({'movies': []}, moviesjson)

        # Create a dictionary for the movies
        movies = {'movies': []}
    else:
        # Load the dictionary from json file
        with open('movies.json') as f:
            movies_temp = json.load(f)

        # Create a dictionary for the movies
        movies = {'movies': []}

        # Load data from file into created movies dictionary
        for i in range(0, len(movies_temp)):
            movies['movies'].append(movies_temp[i])

    # Process N films of IMDb
    logger.info('Movie retrieval started.')
    for i in range(START_ID, MAX_ITERATIONS / 50):
        # Calculate pagination
        pagination = (i * 50) + 1

        # Define url
        url = 'http://www.imdb.com/search/title?sort=num_votes&start=' + str(pagination) + '&title_type=feature'
        logger.info('Started scrapping of ' + url + '.')

        # Process page of 50 movies
        movie = process_page(url)
        logger.info('Finished scrapping of ' + url + '.')

    # Store the updated movies dictionary in the json file (after all movies were retrieved)
    if args.storing == 'unsave':
        gen_json(movies)
        logger.info('All retrieved movies were stored in "movies.json".')

    # Remove the wrapping dictionary
    clean_json()
    logger.info('"movies.json" cleaned up.')

logger.info('Movie retrieval finished.')
"""