import os
import ssl
from datetime import datetime
from sys import stderr
from urllib.parse import quote

import feedparser
import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists
from urllib3.exceptions import InsecureRequestWarning

RSS_MEDIAKUB = 'https://mediakub.net/rss'
RSS_NEWGUBAKHA = 'http://newgubakha.ru/index.php?option=com_ninjarsssyndicator&feed_id=1&format=raw'
RSS_NASHAGUBAHA = 'https://nashagubaha.ru/feed/'
HTML_GUBAKHAOKRUG = 'http://gubakhaokrug.ru/okrug/'
HTML_GUBAKHAOKRUG_SECTIONS = ['novosti', 'media/fotogalereya']
# HTML_NASHAGUBAHA = 'https://nashagubaha.ru/category/'
# HTML_NASHAGUBAHA_SECTIONS = ['cover-stories', 'leisure', 'life', 'health', 'pogoda', 'proisschestviya', 'statyi']
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) '
                  'Version/7.0.3 Safari/7046A194A '
}

Base = declarative_base()


def url_exists(url):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    r = requests.get(url, headers=HEADER, verify=False)
    if r.status_code == 200:
        return True
    else:
        return False


class Parser:
    def __init__(self):
        try:
            self.site1 = RssParser(RSS_MEDIAKUB)
            self.site2 = RssParser(RSS_NEWGUBAKHA)
            self.site3 = Gubakhaokrug(HTML_GUBAKHAOKRUG, HTML_GUBAKHAOKRUG_SECTIONS)
            self.site4 = RssParser(RSS_NASHAGUBAHA)
        except Exception as e:
            print(e, file=stderr)

    def run(self):
        return self.site1.feed_parser() + self.site2.feed_parser() + self.site3.html_parser() + self.site4.feed_parser()


class RssParser:
    def __init__(self, rss_url):
        if url_exists(rss_url):
            try:
                if hasattr(ssl, '_create_unverified_context'):
                    ssl._create_default_https_context = ssl._create_unverified_context
                self.d = feedparser.parse(
                    rss_url
                )
            except Exception as e:
                print(e, file=stderr)

    def feed_parser(self):
        try:
            rez = []
            for entry in self.d['entries']:
                rez.append({'title': entry['title'], 'url': quote(entry['link'], safe='/:')})
            return rez
        except Exception as e:
            print(e, file=stderr)


class HtmlParser:
    def __init__(self, html_url, sections):
        try:
            self.html_url = html_url
            self.sections = sections
        except Exception as e:
            print(e, file=stderr)


class Gubakhaokrug(HtmlParser):
    def html_parser(self):
        if url_exists(self.html_url):
            try:
                rez = []
                for section in self.sections:
                    r = requests.get(self.html_url + section, headers=HEADER)
                    soup = BeautifulSoup(r.content, 'html.parser')
                    if section in 'novosti':
                        elements = soup.find_all('a', attrs={'class': 'news__title'})
                        for elem in elements:
                            rez.append({'title': elem.string, 'url': 'http://gubakhaokrug.ru' + elem['href']})
                    else:
                        elements = soup.find_all('a', attrs={'class': 'fotoalbum__text-title'})
                        for elem in elements:
                            rez.append({'title': elem.string, 'url': 'http://gubakhaokrug.ru' + elem['href']})
                return rez
            except Exception as e:
                print(e, file=stderr)


class Nashagubaha(HtmlParser):
    def html_parser(self):
        if url_exists(self.html_url):
            try:
                rez = []
                for section in self.sections:
                    r = requests.get(self.html_url + section, headers=HEADER)
                    soup = BeautifulSoup(r.content, 'html.parser')
                    elements = soup.find_all('h2', attrs={'class': 'entry-title'})
                    for elem in elements:
                        if {'title': elem.a.string, 'url': elem.a['href']} in rez:
                            continue
                        else:
                            rez.append({'title': elem.a.string, 'url': elem.a['href']})
                return rez
            except Exception as e:
                print(e, file=stderr)


class DataBase:
    def __init__(self, file_name):
        try:
            self.engine = create_engine(f'sqlite:///{os.getcwd()}/{file_name}.sqlite')
            if database_exists(self.engine.url) is False:
                Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(e, file=stderr)

    def all_from_db(self):
        rez = []
        session = self.Session()
        for row in session.query(NewsUrl).all():
            rez.append({'title': row.title, 'url': row.url})
        session.close()
        return rez

    def titles_from_db(self):
        rez = []
        session = self.Session()
        for row in session.query(NewsUrl).all():
            rez.append(row.title)
        session.close()
        return rez

    def urls_from_db(self):
        rez = []
        session = self.Session()
        for row in session.query(NewsUrl).all():
            rez.append(row.url)
        session.close()
        return rez

    def add_to_db(self, item):
        session = self.Session()
        session.add(NewsUrl(title=item['title'], url=item['url']))
        session.commit()
        session.close()


class NewsUrl(Base):
    __tablename__ = 'news_urls'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False, default=datetime.now())
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return "<NewsUrl(id='%s', datetime='%s', title='%s', url='%s')>" % (
            self.id, self.datetime, self.title, self.url)


if __name__ == '__main__':
    p = Parser()
    print(p.run())
