import argparse
import os
from bs4 import BeautifulSoup
from datetime import datetime
from googleapi_connection import GoogleAPI
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


def _get_live_feed():
    """
    Gets details of live feed.
    Due to performance reasons, it first checks the status of live feed,
    if it's not changed, doesn't do any http get calls to individual movies

    :return: Only New Data, List of List with columns [Type, Name, Description, Date]
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

        data.append([type, title_tag.string, " ".join(desc_parts), date])

    _feed_urls = updated_urls
    return data


def _search_in_movie_db(query, date):
    """
    Searches a movie or series in movie database based on query and release date
    :param query: Query in format of link
    :param date: Release date of given movie or series
    :return: The movie database link if it founds, otherwise None
    """
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
            return result_link.split('?')[0].split('/')[2]  # Extracts Key from URL
    return None


def _sent_to_database(data):
    api = GoogleAPI()
    api.authenticate('credentials.json')
    if os.path.exists('spreadsheet_id.txt'):
        with open("spreadsheet_id.txt", 'r') as f:
            api.spreadsheetID = f.readline()
        api.append_spreadsheet(api.spreadsheetID, 'A1:D1', data)
    else:
        new_id = api.create_spreadsheet('Movie Data')
        print(new_id)
        with open('spreadsheet_id.txt', 'w+') as f:
            f.write(new_id)
        api.append_spreadsheet(new_id, 'A1:D1', data)
    del api


def scrape():
    start_time = time.time()
    new_data = _get_live_feed()
    if new_data:
        for data in new_data:
            query = _construct_movie_query(type=data[0], name=data[1])
            date = datetime.strptime(data[3], "%d-%m-%Y")
            key = _search_in_movie_db(query, date)
            data.append(key)
        _sent_to_database(new_data)
    print("---Scraping is done in {:.2f} seconds ---".format(time.time() - start_time))


def main():
    parser = argparse.ArgumentParser(description='Help Screen for Command Line Arguments')
    parser.add_argument("--sec", default=600, type=int, help="Sleep time in seconds for scraper")

    args = parser.parse_args()

    scrape()
    time.sleep(args.sec)
    main()


if __name__ == '__main__':
    main()
