import requests
import xmltodict
import os

from bs4 import BeautifulSoup


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
    print(res.url)

    data = xmltodict.parse(res.text)
    try:
        books = data['GoodreadsResponse']['search']['results']['work']
    except TypeError:
        return None
    result = []
    if type(books) is not list:
        books = [books]
    for item in books[:3]:
        book = {}
        book['isbn'] = item['best_book']['id']['#text']
        book['title'] = item['best_book']['title']
        book['author'] = item['best_book']['author']['name']
        try:
            book['rating'] = float(item['average_rating'])
        except Exception:
            book['rating'] = None
        book['image_url'] = item['best_book']['image_url']
        book['prices'] = get_tiki_price(book['title'], book['author'])
        result.append(book)
    return result


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
    results = []
    for item in books[:6]:
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
            continue
        if compare_name(book['author'], author):
            results.append(book)
    return results
