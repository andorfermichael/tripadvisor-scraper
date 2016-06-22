import argcomplete
import argparse
import json
import logging
import sys
import requests
import time
from functools import wraps
import os
import csv
from bs4 import BeautifulSoup


# Get all pagination urls of the city
def parse_pagination_urls_of_city(city_default_url, city_url, offset, header):
    # Initialize the list for the resulting urls
    pagination_urls = list()

    # Retrieve url content of city (first page)
    content = requests.get(city_url, header).content

    # Define parser
    soup = BeautifulSoup(content, 'html.parser')

    # Scrape number of pages (pagination of hotels in the city)
    number_of_pages_in_city = 1#soup.find('a', attrs={'class': 'last'}).contents[0]

    for i in range(0, int(number_of_pages_in_city)):
        if i == 0:
            # Append the already available first page url
            pagination_urls.append(city_default_url)
        else:
            # Calculate the dash positions
            occurences_of_dash = [j for j in range(len(city_default_url)) if city_default_url.startswith('-', j)]

            # Get the second dash position
            second_dash_index = occurences_of_dash[1]

            # Each page contains 30 hotels
            city_pagination = i * offset

            # Build the current page url and append it to the list
            current_city_pagination_url = city_default_url[:second_dash_index] + '-oa' + str(city_pagination) + city_default_url[second_dash_index:] + '#ACCOM_OVERVIEW'
            pagination_urls.append(current_city_pagination_url)

    return pagination_urls


# Get all hotel urls of the city
def parse_hotel_urls_of_city(base_url, pagination_urls, header):
    # Initialize the list for the resulting urls
    hotel_urls = list()

    for pagination_url in pagination_urls[0:1]:
        # Build url out of base and current page url
        city_pagination_url = base_url + pagination_url

        # Retrieve url content of the page url
        content = requests.get(city_pagination_url, header).content

        # Define parser
        soup = BeautifulSoup(content, 'html.parser')

        # Store each hotel url in the list
        for j, city_hotel_url in enumerate(soup.find_all('a', attrs={'class': 'property_title'})):
            hotel_urls.append(base_url + soup.find_all('a', attrs={'class': 'property_title '})[j]['href'][1:])

    # Remove duplicates
    hotel_urls = set(hotel_urls)
    hotel_urls = list(hotel_urls)

    return hotel_urls


# Get all pagination urls for all given hotels
def parse_pagination_urls_of_hotel(hotel_urls, header):
    # Initialize the list for the resulting urls
    pagination_urls = list()

    for hotel_url in hotel_urls[0:1]:
        # Retrieve url content of the page url
        content = requests.get(hotel_url, header).content

        # Define parser
        soup = BeautifulSoup(content, 'html.parser')

        # Scrape the highest pagination value of a hotel's pages
        pagination_items = soup.find_all('a', attrs={'class': 'pageNum'})
        maximum_pagination_of_hotel = int(pagination_items[-1].contents[0])

        # Calculate all pagination urls of the hotel
        for i in range(0, maximum_pagination_of_hotel):
            if i == 0:
                # Append the already available first page url
                pagination_urls.append(hotel_url + '#REVIEWS')
            else:
                # Calculate the dash positions
                occurrences_of_dash = [j for j in range(len(hotel_url)) if hotel_url.startswith('-', j)]

                # Get the fourth dash position
                fourth_dash_index = occurrences_of_dash[3]

                # Each page contains 10 hotels
                hotel_pagination = i * 10

                # Build the current page url and append it to the list
                hotel_page_url = hotel_url[:fourth_dash_index] + '-or' + str(hotel_pagination) + hotel_url[fourth_dash_index:] + '#REVIEWS'
                pagination_urls.append(hotel_page_url)

    return pagination_urls


# Get all review urls of all given hotels
def parse_review_urls_of_hotel(base_url, pagination_urls, header):
    # Initialize the list for the resulting urls
    review_urls = list()

    for pagination_url in pagination_urls[0:1]:
        # Retrieve url content of the hotel pagination url
        content = requests.get(pagination_url, header).content

        # Define parser
        soup = BeautifulSoup(content, 'html.parser')

        # Get all review containers of the current page
        hotel_review_containers = soup.find_all('div', attrs={'class': 'basic_review'})

        # Retrieve each review url of the current hotel pagination page
        for hotel_review_container in hotel_review_containers:
            quote = hotel_review_container.find('div', attrs={'class': 'quote'})

            # Get the review url without base url
            review_url = quote.find('a')['href'][1:]

            # Append the complete review url to the list
            review_urls.append(base_url + review_url)

    return review_urls


# Parse all reviews of a city
def parse_reviews_of_city(review_urls, city_default_url, user_base_url, header):
    processed_hotels = list()
    hotel_information = dict()

    # Create a folder for the current scrapping session
    city_directory_path = create_session_directory(city_default_url)

    for review_url in review_urls[0:1]:
        # Calculate the dash and point positions
        occurrences_of_dash = [j for j in range(len(review_url)) if review_url.startswith('-', j)]
        occurrences_of_point = [j for j in range(len(review_url)) if review_url.startswith('.', j)]

        # Get the hotel name out of the url
        hotel_name = review_url[occurrences_of_dash[3] + 1:occurrences_of_point[2]]

        # Only process hotel information once
        if hotel_name not in processed_hotels:
            processed_hotels.append(hotel_name)
            hotel_information = parse_hotel_information(review_url, header)
            hotel_directory_path = create_hotel_directory(hotel_information['name'].replace(' ', '_').lower(), city_directory_path)
            store_hotel_data(hotel_information, hotel_directory_path)
            #print(hotel_information)

        # Parse review information
        #review_information = parse_review_information(review_url, user_base_url, header)

    #store_data(hotel_information, review_information, city_default_url)



# Creates a csv file for a hotel and stores the hotel information inside
def store_hotel_data(hotel_data, hotel_directory_path):
    with open(hotel_directory_path + '/' + hotel_data['name'].replace(' ', '_').lower() + '-information.csv', 'w', newline='') as file:
        # Setup a writer
        csvwriter = csv.writer(file, delimiter='|')

        # Write headlines into the file
        csvwriter.writerow(['Name', 'Address', 'Description' , 'Stars', 'Room Count ', 'Amenities', 'TripAdvisor City Rank', 'Overall Rating' , 'Review Count', 'Review Rating Count', 'Review Reason Count', 'Reviewer Languages'])

        # Build the record
        record = hotel_data['name'] + '|' + hotel_data['address'] + '|' + hotel_data['description'] + '|' + hotel_data['stars'] + '|' + \
                 hotel_data['room-count'] + '|' + hotel_data['amenities'] + '|' + hotel_data['rank'] + '|' + \
                 hotel_data['overall-rating'] + '|' + hotel_data['review-count'] + '|' + hotel_data['star-filter'] + '|' + \
                 hotel_data['reason-filter'] + '|' + hotel_data['reviewer-languages']

        # Write the data into the file
        csvwriter.writerow([record])

# Creates a directory for a hotel
def create_hotel_directory(hotel_name, city_directory_name):
    # Build directory name
    directory_path = city_directory_name + '/' + hotel_name

    # Create the folder
    os.makedirs(directory_path)

    return directory_path

# Creates a directory for a session
def create_session_directory(city_default_url):
    # Get the current time
    timestr = time.strftime('%Y%m%d-%H%M%S')

    # Get the city name from the url
    occurrences_of_dash = [j for j in range(len(city_default_url)) if city_default_url.startswith('-', j)]
    city_name = city_default_url[occurrences_of_dash[1] + 1:occurrences_of_dash[2]].lower()

    # Build directory name
    directory_path = 'data/' + timestr + '-' + city_name

    # Create the folder
    os.makedirs(directory_path)

    return directory_path


def parse_hotel_information(review_url, header):
    # Initialize the dictionary for the hotel
    hotel = dict()

    # Retrieve url content of the review url
    content = requests.get(review_url, header).content

    # Define parser
    soup = BeautifulSoup(content, 'html.parser')

    hotel['name'] = soup.find('a', attrs={'class': 'HEADING'}).text.strip()
    hotel['overall-rating'] = soup.find('img', attrs={'class': 'sprite-rating_no_fill'})['alt'][0:1] + ' stars'
    hotel['rank'] = soup.find('div', attrs={'class': 'slim_ranking'}).text.strip()

    review_count = soup.find('h3', attrs={'class': 'reviews_header'}).text
    occurrences_of_spaces = [j for j in range(len(review_count)) if review_count.startswith(' ', j)]
    hotel['review-count'] = review_count[0:occurrences_of_spaces[0]]

    review_filter = soup.find('fieldset', attrs={'class': 'review_filter_lodging'})
    star_filter_items = review_filter.find('div', attrs={'class': 'col2of2'}).find_all('div', attrs={'class': 'wrap'})
    reason_filter_items = review_filter.find('div', attrs={'class': 'trip_type'}).find_all('div', attrs={'class': 'segment'})
    star_filter_string = ''
    reason_filter_string = ''

    for star_filter_item in star_filter_items:
        description = star_filter_item.find('span', attrs={'class': 'text'}).text
        count = star_filter_item.find('span', attrs={'class': 'compositeCount'}).text
        star_filter_string += description + ' (' + count + ') - '

    for reason_filter_item in reason_filter_items:
        description = reason_filter_item.find('div', attrs={'class': 'filter_selection'}).text
        count = reason_filter_item.find('div', attrs={'class': 'value'}).text
        reason_filter_string += description + ' (' + count + ') - '

    hotel['star-filter'] = star_filter_string[0:-3]
    hotel['reason-filter'] = reason_filter_string[0:-3]

    language_items = soup.find('select', attrs={'id': 'filterLang'}).find_all('option')[:-1]
    languages = ''

    for language_item in language_items:
        languages += language_item.text.replace('first', '').strip() + ', '

    hotel['reviewer-languages'] = languages[:-2]

    hotel['address'] = soup.find('span', attrs={'class': 'format_address'}).text.replace('|', '-')

    try:
        amenity_items = soup.find('div', attrs={'class': 'indent'}).find_all('span', attrs={'class': 'amenity'})
        amenities = ''

        for amenity_item in amenity_items:
            amenities += amenity_item.text + ', '

        hotel['amenities'] = amenities[:-2]
    except:
        hotel['amenities'] = 'n.a.'

    hotel['stars'] = soup.find('div', attrs={'class': 'stars'}).text.replace('Hotel Class:', '').strip()[0:1]

    hotel['room-count'] = soup.find('span', attrs={'class': 'tabs_num_rooms'}).text.strip()

    try:
        hotel['description'] = soup.find('span', attrs={'class': 'descriptive_text'}).text.strip() + soup.find('span', attrs={'class': 'descriptive_text_last'}).text.strip()
    except:
        hotel['n.a.']

    return hotel


# Parse all information of a review
def parse_review_information(review_url, user_base_url, header):
    # Initialize the dictionary for the review
    review = dict()

    # Retrieve url content of the review url
    content = requests.get(review_url, header).content

    # Define parser
    soup = BeautifulSoup(content, 'html.parser')

    # Parse the container which contains the whole review content and meta information
    review_container = soup.find('div', attrs={'class': 'reviewSelector'})

    # Parse the container which contains the user information
    user_container = review_container.find('div', attrs={'class': 'col1of2'})

    # Parse the container which contains the review information
    entry_container = review_container.find('div', attrs={'class': 'col2of2'})

    # Parse review information

    review['title'] = entry_container.find('div', attrs={'class': 'quote'}).text
    review['rating'] = entry_container.find('img', attrs={'class': 'sprite-rating_s_fill'})['alt'][0:1]
    review['date'] = entry_container.find('span', attrs={'class': 'ratingDate'})['content']
    review['text'] = entry_container.find('div', attrs={'class': 'entry'}).find('p').text

    try:
        stay = entry_container.find('span', attrs={'class': 'recommend-titleInline'}).text
        occurences_of_colon = [j for j in range(len(stay)) if stay.startswith(',', j)]
        review['time'] = stay[0:occurences_of_colon[0]].replace('Stayed ', '')
        review['reason'] = stay[occurences_of_colon[0] + 2:].replace('traveled ', '')
    except:
        review['time'] = 'n.a.'
        review['reason'] = 'n.a.'

    try:
        review['helpful-votes'] = entry_container.find('span', attrs={'class': 'numHlpIn'}).text
    except:
        review['helpful-votes'] = 0

    try:
        review['room-tip'] = entry_container.find('div', attrs={'class': 'inlineRoomTip'}).text
    except:
        review['room-tip'] = 'n.a.'

    try:
        # Set all to n.a. per default so that it has an informative value in each case
        review['value-rating'] = 'n.a.'
        review['location-rating'] = 'n.a.'
        review['rooms-rating'] = 'n.a.'
        review['cleanliness-rating'] = 'n.a.'
        review['service-rating'] = 'n.a.'
        review['business-rating'] = 'n.a.'
        review['check-rating'] = 'n.a.'
        review['sleep-rating'] = 'n.a.'

        recommendation_columns = entry_container.find('ul', attrs={'class': 'recommend'}).find('li').find_all('ul',attrs={'class': 'recommend-column'})

        for column in recommendation_columns:
            recommend_answers = column.find_all('li', attrs={'class': 'recommend-answer'})

            for answer in recommend_answers:
                recommend_description = answer.find('div', attrs={'class': 'recommend-description'}).text
                rating = answer.find('img', attrs={'class': 'sprite-rating_ss_fill'})['alt'][0:1]

                if recommend_description == 'Value':
                    review['value-rating'] = rating
                elif recommend_description == 'Location':
                    review['location-rating'] = rating
                elif recommend_description == 'Rooms':
                    review['rooms-rating'] = rating
                elif recommend_description == 'Cleanliness':
                    review['cleanliness-rating'] = rating
                elif recommend_description == 'Service':
                    review['service-rating'] = rating
                elif recommend_description == 'Business service (e.g., internet access)':
                    review['business-rating'] = rating
                elif recommend_description == 'Check in / front desk':
                    review['check-rating'] = rating
                elif recommend_description == 'Sleep Quality':
                    review['sleep-rating'] = rating

    except:
        # Log here
        print("")

    # Parse user information
    user_name = user_container.find('div', attrs={'class': 'username'}).find('span', attrs={'class': 'scrname'}).text
    reviewer = parse_reviewer_information(user_name, user_base_url, header)

    return [review, reviewer]


# Parse the profile information of a reviewer
def parse_reviewer_information(user_name, user_base_url, header):
    # Initialize the dictionary for the user
    user = dict()

    # Define the user profile url
    profile_url = user_base_url + user_name

    # Retrieve url content of the user url
    content = requests.get(profile_url, header).content

    # Define parser
    soup = BeautifulSoup(content, 'html.parser')

    user['name'] = user_name

    try:
        user['level'] = soup.find('div', attrs={'class': 'level'}).find('span').text
    except:
        user['level'] = 'n.a'

    try:
        user['since'] = soup.find('div', attrs={'class': 'ageSince'}).find_all('p')[0].text
    except:
        user['since'] = 'n.a.'

    try:
        user['demographic'] = soup.find('div', attrs={'class': 'ageSince'}).find_all('p')[1].text
    except:
        user['demographic'] = 'n.a.'

    try:
        user['hometown'] = soup.find('div', attrs={'class': 'hometown'}).find('p').text
    except:
        user['hometown'] = 'n.a.'

    try:
        number_of_reviews = soup.find_all('a', attrs={'data-filter': 'REVIEWS_ALL'})[0].contents[0]
        occurences_of_space = [j for j in range(len(number_of_reviews)) if number_of_reviews.startswith(' ', j)]
        user['reviews'] = number_of_reviews[0:occurences_of_space[0]]
    except:
        user['reviews'] = 'n.a.'

    try:
        number_of_ratings = soup.find('a', attrs={'data-filter': 'RATINGS_ALL'}).contents[0]
        occurences_of_space = [j for j in range(len(number_of_ratings)) if number_of_ratings.startswith(' ', j)]
        user['ratings'] = number_of_ratings[0:occurences_of_space[0]]
    except:
        user['ratings'] = 'n.a.'

    try:
        number_of_photos = soup.find('a', attrs={'data-filter': 'PHOTOS_ALL'}).contents[0]
        occurences_of_space = [j for j in range(len(number_of_photos)) if number_of_photos.startswith(' ', j)]
        user['photos'] = number_of_photos[0:occurences_of_space[0]]
    except:
        user['photos'] = 'n.a.'

    try:
        number_of_helpful_votes = soup.find_all('a', attrs={'data-filter': 'REVIEWS_ALL'})[1].contents[0]
        occurences_of_space = [j for j in range(len(number_of_helpful_votes)) if number_of_helpful_votes.startswith(' ', j)]
        user['helpfuls'] = number_of_helpful_votes[0:occurences_of_space[0]]
    except:
        user['helpfuls'] = 'n.a.'

    try:
        tags = ''
        tag_bubbles = soup.find_all('div', attrs={'class': 'tagBlock'}).find_all('div', attrs={'class': 'tagBubble'})

        for tag_bubble in tag_bubbles:
            tags += tag_bubble.text + ', '

        user['tags'] = tags
    except:
        user['tags'] = 'n.a.'

    return user


# Main
if __name__ == '__main__':
    # Define user agent
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0'}

    # Define base url of TripAdvisor
    BASE_URL = 'http://www.tripadvisor.com/'

    # TODO: Load from file or enter via commandline
    CITY_DEFAULT_URL = 'Hotels-g293974-Istanbul-Hotels.html'
    CITY_URL = BASE_URL + CITY_DEFAULT_URL

    USER_BASE_URL = 'https://www.tripadvisor.com/members/'

    # Define items per page
    number_of_hotels_per_page = 30
    number_of_reviews_per_page = 10

    # Parse all needed urls
    city_pagination_urls = parse_pagination_urls_of_city(CITY_DEFAULT_URL, CITY_URL, number_of_hotels_per_page, headers)
    city_hotel_urls = parse_hotel_urls_of_city(BASE_URL, city_pagination_urls, headers)
    hotel_pagination_urls = parse_pagination_urls_of_hotel(city_hotel_urls, headers)
    city_review_urls = parse_review_urls_of_hotel(BASE_URL, hotel_pagination_urls, headers)
    #print(city_review_urls)

    # Store all reviews of the city
    parse_reviews_of_city(city_review_urls, CITY_DEFAULT_URL, USER_BASE_URL, headers)