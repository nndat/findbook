import requests
import xmltodict
import os

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

MAXFIND = 3


def compare_name(name1, name2):
    name1 = name1.lower()
    name2 = name2.lower()
    if name1 == name2:
        return True
    if name1 in name2 or name2 in name1:
        return True
    name1 = name1.split()
    name2 = name2.split()
    if name1[0] == name2[0] and name1[-1] == name2[-1]:
        return True
    return False


def get_books(name):
    url = 'https://www.goodreads.com/search/index.xml'
    key = os.environ.get('GOODREADS_KEY')
    param = {'key': key, 'q': name}
    res = requests.get(url, params=param)

    data = xmltodict.parse(res.text)
    try:
        books = data['GoodreadsResponse']['search']['results']['work']
    except TypeError:
        return None
    if type(books) is not list:
        books = [books]

    with ThreadPoolExecutor() as excutor:
        results = excutor.map(getbook, books[:3])
    return results


def getbook(item):
    book = {}
    book['isbn'] = item['best_book']['id']['#text']
    book['title'] = item['best_book']['title']
    book['author'] = item['best_book']['author']['name']
    try:
        book['rating'] = float(item['average_rating'])
    except Exception:
        book['rating'] = None
    book['image_url'] = item['best_book']['image_url']
    with ThreadPoolExecutor() as excutor:
        tiki = excutor.submit(get_tiki_price,
                              book['title'], book['author'])
        vina = excutor.submit(get_vinabook_price,
                              book['title'], book['author'])
        book['prices'] = tiki.result() + vina.result()
    return book


def get_tiki_price(title, author):
    url = 'https://tiki.vn/search'
    params = {'q': title}
    res = requests.get(url, params=params)
    soup = BeautifulSoup(res.text, 'html.parser')

    books = soup.find_all(
        'div',
        {'class': 'product-item search-div-product-item'}
    )
    if len(books) == 0:
        return []
    with ThreadPoolExecutor() as excutor:
        results = excutor.map(tiki_search, books[:MAXFIND])
    results = [book for book in results
               if book and compare_name(book['author'], author)]
    return results


def tiki_search(item):
    book = {}
    book['trading'] = 'Tiki'
    try:
        book['title'] = item.find('p', {'class': 'title'}).text.strip()
        book['author'] = item.find('p', {'class': 'author'}).text.strip()
        book['price'] = item.find('span', {'class': 'final-price'})\
                            .text.strip()
        book['link'] = item.find('a')['href']
        book['img_url'] = item.find(
            'img',
            {'class': 'product-image img-responsive'})['src']
    except Exception:
        return None
    return book


def get_vinabook_price(title, author):
    url = 'https://www.vinabook.com'
    params = {'q': title}
    res = requests.get(url, params=params)
    soup = BeautifulSoup(res.text, 'html.parser')

    books = soup.find_all('td', {"class": "compact border-bottom"})
    if len(books) == 0:
        return []
    with ThreadPoolExecutor() as excutor:
        results = excutor.map(vinabook_search, books[:MAXFIND])
    results = [book for book in results
               if book and compare_name(book['author'], author)]
    return results


def vinabook_search(item):
    book = {}
    book['trading'] = 'Vinabook'
    try:
        book['title'] = item.find('a', {'class': 'product-title'})\
                            .text.strip()
        book['author'] = item.find('span', {'class': 'author'})\
                             .text.strip()
        book['price'] = item.find('span', {'class': 'price'}).text.strip()
        book['link'] = item.find('a', {'class': 'product-title'})['href']
        book['img_url'] = item.find_all('img')[-1]['src']
    except Exception:
        return None
    return book
