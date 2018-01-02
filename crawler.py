from typing import NamedTuple

from bs4 import BeautifulSoup
import requests

BASE_URL = 'http://maria.catholic.or.kr/bible/read/bible_read.asp'
PAYLOAD = {
    'm': 2,  # 1: 구약성경, 2: 신약성경 ...
    'n': 147,  # 전체 성경 각 권의 pk 값
    'p': 1,  # 페이지
}


class BibleInfo(NamedTuple):
    gospels: str
    chapters: int
    paragraphs: int
    contents: str


def requests_from_catholic_goodnews(url, payload):
    """
    가톨릭 굿뉴스 사이트에서 리퀘스트 객체를 받아온다
    :param url: request를 받을 url
    :param payload: parameter 값
    :return: requests 객체
    """
    return requests.get(url, params=payload)


def soup_from_requests(requests):
    """
    리퀘스트 객체에서 soup 객체를 받아온다
    :param requests: requests 객체
    :return: soup 객체
    """
    text = requests.text
    return BeautifulSoup(text, 'lxml')


def primary_key_of_gospel(soup):
    """
    soup 객체에서 복음서 이름과 고유 번호를 가져와 OrderedDict를 생성한다
    :param soup: soup 객체
    :return: 복음서 이름과 고유 번호의 OrderedDict
    """
    contents = soup


def texts_from_soup(soup):
    """
    soup 객체에서 성경 구절 텍스트 제너레이터 컴프리헨션을 생성한다
    :param soup: soup 객체
    :return: 성경 구절 리스트
    """
    contents = soup.select_one('#container > .type3 > #scrapSend > #font_chg > tbody')

    raw_texts = contents.find_all('td', attrs={'class': 'tt'})
    strip_texts = [i.text.strip() for i in raw_texts]

    raw_paragraphs = contents.find_all('td', attrs={'class': 'num_color'})
    strip_paragraphs = [p.text.strip() for p in raw_paragraphs]
    return ((item[1], item[0]) for item in zip(strip_texts, strip_paragraphs))


def make_namedtuple(gen):
    """
    list에 복음서와 구절을 입혀 네임드튜플로 저장한다
    :param gen: 성경 구절과 넘버 제너레이터
    :return:
    """
    return


if __name__ == '__main__':
    r = requests_from_catholic_goodnews(BASE_URL, PAYLOAD)
    print(r)
    s = soup_from_requests(r)
    # print(s)
    t = texts_from_soup(s)
    print(t)
