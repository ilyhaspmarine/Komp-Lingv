import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
from time import sleep
from fake_useragent import UserAgent
from selenium import webdriver
import cfscrape

def find_document(collection, elements, multiple=False):
    """ Function to retrieve single or multiple documents from a provided
    Collection using a dictionary containing a document's elements.
    """
    if multiple:
        results = collection.find(elements)
        return [r for r in results]
    else:
        return collection.find_one(elements)

def parse(url, series_collection):
    sleep(5)
    print('Приступаю')
    scraper = cfscrape.create_scraper()
    list = {}

    try:
        html = scraper.get(url)
    except Exception:
        sleep(30)
        html = scraper.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    if soup is not None:

        try:
            news_date = soup.find('div', class_='date').text.replace('сегодня: ', '')
        except:
            news_date = None

        try:
            news_title = soup.find('h1').text
        except:
            news_title = None

        try:
            detail = soup.find('div', class_='news-detail')
        except:
            detail = None

        if detail is not None:
            first_text = detail.find('p')
            check_first_text = detail.find('p', attrs={"style": "text-align: justify;"})
            full_text = detail.findAll('p', attrs={"style": "text-align: justify;"})
            if first_text == check_first_text:
                red_full_text = first_text.text
            else:
                red_full_text = ""
            for frase in full_text:
                red_full_text = red_full_text + str(frase.text)
            red_full_text = re.sub(r'\s+', ' ', red_full_text)

            author = detail.find('p', attrs={"style": "text-align: right;"})

            list['Ссылка на новость'] = url
            list['Заголовок'] = news_title
            news_date = re.sub(r'\s+', ' ', news_date)
            list['Дата публикации'] = news_date
            list['Текст статьи'] = red_full_text
            if author is not None:
                author = re.sub(r'\s+', ' ', author.text)
                list['Автор статьи'] = author
            else:
                list['Автор статьи'] = "Не указан"

            find_news = find_document(series_collection, {'Ссылка на новость': url})
            if find_news is None:
                series_collection.insert_one(list)
                print('Успешно записал в базу')
        else:
            print('С этой новостью ошибка', url)

    sleep(10)

    return list

def getPageCount(soup):
    paggination = soup.find('div', class_='modern-page-navigation')
    return int(paggination.find_all('a')[-2].text)

def scanPage(url, series_collection):
    try:
        news_page = scraper.get(url)
    except Exception:
        print('Ошибка при подключении...')
        sleep(300)
        news_page = scraper.get(url)
    soup_n = BeautifulSoup(news_page.text, 'html.parser')
    news_list = soup_n.find("div", class_="row news-items")
    offerURLs = news_list.findAll("a")
    for item in offerURLs:
        href = item.attrs['href']
        if "%" in href:
            href = href[:href.find("%")]
        if 'http:' in href or 'https:' in href:
            if 'gubernator' in href or 'news' in href:
                result = parse(href, series_collection)
            else:
                print('Необычная ссылка', href)
        else:
            href = "http://www.volgograd.ru" + item.attrs["href"]
            result = parse(href, series_collection)


def scanSection(url, series_collection):
    try:
        main_page = scraper.get(exampleURL)
    except Exception:
        print('Ошибка при подключении...')
        sleep(300)
        main_page = scraper.get(exampleURL)
    soup = BeautifulSoup(main_page.text, 'html.parser')
    pageCount = getPageCount(soup)
    print('Всего страниц найдено %d' % pageCount)
    for page in range(1, pageCount):
        sleep(15)
        print('Парсинг %d%%' % (page / pageCount * 100))
        https = (url + '/?PAGEN_1=%d' % page)
        scanPage(https, series_collection)
        sleep(15)

if __name__ == '__main__':
    scraper = cfscrape.create_scraper()

    client = MongoClient("localhost", 27017)
    db = client['NewsDataBase']
    series_collection = db['News_parse']

    exampleURL = "http://www.volgograd.ru/news"

    scanSection(exampleURL, series_collection)
