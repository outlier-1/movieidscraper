from bs4 import BeautifulSoup
import requests

STREAM_SOURCE_URL = 'https://hdss.to/'


def _get_feed_urls():
    """ Gets the URL's for individual series or film,
    Lightweight function

    :return: List of URL's for each series or film.
    """
    urls = []
    request = requests.get(STREAM_SOURCE_URL)
    soup = BeautifulSoup(request.content, features="html.parser")
    for li in soup.find_all(name='li', class_='TPostMv'):
        urls.append(li.a['href'])
    return urls


def get_live_feed():
    """
    Gets details of live feed.
    Due to performance reasons, it first checks the status of live feed,
    if it's not changed, doesn't do any http get calls to individual movies

    :return: Dictionary of Title-Description Pairs of Live Feed
    """
    global _live_feed_urls

    # If the live feed has not changed, return
    updated_urls = _get_feed_urls()
    if updated_urls == _live_feed_urls:
        return

    # If the live feed has changed, get new title-description pairs
    data_dict = {}
    for url in updated_urls:
        request = requests.get(url)
        soup = BeautifulSoup(request.content, features="html.parser")

        title_tag = soup.find('h1', class_='Title')
        desc_tag = soup.find('div', class_='Description')

        desc_parts = []
        for st in desc_tag.stripped_strings:
            desc_parts.append(st)

        data_dict[title_tag.string] = " ".join(desc_parts)

    _live_feed_urls = updated_urls
    return data_dict
