from bs4 import BeautifulSoup
from datetime import datetime
import requests
import codecs
import time

STREAM_SOURCE_URL = 'https://hdss.to/'
MOVIE_DB_SOURCE_URL = 'https://www.themoviedb.org'

_feed_urls = set()


def _get_feed_urls():
    """ Gets the URL's for individual series or film,
    Lightweight function

    :return: List of URL's for each series or film.
    """
    urls = set()
    request = requests.get(STREAM_SOURCE_URL)
    soup = BeautifulSoup(request.content, features="html.parser")
    for li in soup.find_all(name='li', class_='TPostMv'):
        urls.add(li.a['href'])
    return urls


def get_live_feed():
    """
    Gets details of live feed.
    Due to performance reasons, it first checks the status of live feed,
    if it's not changed, doesn't do any http get calls to individual movies

    :return: Only New Data, List of List with columns [Name, Description, Date]
    """
    global _feed_urls

    # Check for Set Difference, If it's empty, feed is same as last time
    updated_urls = _get_feed_urls()
    new_urls = updated_urls - _feed_urls
    if not new_urls:
        return None

    # If the live feed has changed, get new data (set difference)
    data = []
    for url in new_urls:
        request = requests.get(url)
        soup = BeautifulSoup(request.content, features="html.parser")

        title_tag = soup.find('h1', class_='Title')
        desc_tag = soup.find('div', class_='Description')
        info_tag = soup.find('ul', class_='InfoList')

        type = 'tv' if 'serie' in url else 'movie'

        # Concatenates Description Strings
        desc_parts = []
        for st in desc_tag.stripped_strings:
            desc_parts.append(st)

        # Extracting Date Information, Process is different for movies and series
        if type == 'tv':
            for string in info_tag.strings:
                try:
                    dt_obj = datetime.strptime(string, '%d-%m-%Y')
                    date = dt_obj.strftime("%d-%m-%Y")
                    break
                except ValueError:
                    pass
            pass
        else:
            date = list(info_tag.li.strings)[1]

        data.append([title_tag.string, " ".join(desc_parts), date, type])

    _live_feed_urls = updated_urls
    return data


def _construct_movie_query(name, type):
    clean_name = ''
    for ch in name:
        if ch.isalnum():
            clean_name += ch
        else:
            clean_name += '%'
            hex_val = codecs.encode(ch.encode(), "hex")
            clean_name += hex_val.decode().upper()
    query = "{src}/search/{type}?query={name}&language=en-US".format(src=MOVIE_DB_SOURCE_URL,
                                                                      type=type,
                                                                      name=clean_name)
    return query


def search_in_movie_db(query, date):
    """ Get all result list, check with dates """
    request = requests.get(query)
    soup = BeautifulSoup(request.content, features="html.parser")
    for a in soup.find_all('a', class_='title result'):
        date_str = a.find_next_sibling('span').string
        try:
            result_dt = datetime.strptime(date_str, "%B %d, %Y")
        except ValueError:
            pass
        if result_dt == date:
            result_link = a['href']
            return result_link.split('?')[0].split('/')[2]  # Extracts Key
    return None


def sent_to_database(key, data):
    with open('new.txt', 'a+') as f:
        f.write("{}\t{}\t{}\n".format(data[0], data[1], key))


def scrape():
    new_data = get_live_feed()
    if new_data:
        for data in new_data:
            query = _construct_movie_query(name=data[0], type=data[3])
            date = datetime.strptime(data[2], "%d-%m-%Y")
            key = search_in_movie_db(query, date)
            sent_to_database(key, data)
    time.sleep(600)
    scrape()

scrape()