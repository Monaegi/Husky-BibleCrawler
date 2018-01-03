from typing import NamedTuple
from urllib.parse import parse_qsl

from bs4 import BeautifulSoup
import requests

BASE_URL = 'http://maria.catholic.or.kr/bible/read/bible_read.asp'
PAYLOAD = {
    'm': 2,  # 1: 구약성경, 2: 신약성경 ...
    'n': 147,  # 전체 성경 각 권의 pk 값
    'p': 1,  # 페이지
}


class BibleInfo(NamedTuple):
    gospels: str  # 성경책
    chapters: int  # 장
    paragraphs: str  # 절
    contents: str  # 본문


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
    soup 객체에서 복음서 이름과 고유 번호를 가져와 Dict를 생성한다
    :param soup: soup 객체
    :return: 복음서 이름과 고유 번호의 Dict
    """
    contents = soup.select('#container > .list_c2 > li > .list_c2_sub > li > a')

    links = (i.get('href') for i in contents)
    parse = (parse_qsl(i) for i in links)
    pk_lists = (i[1] for i in parse)

    keywords = (i.get_text() for i in contents)

    dic = {int(i[0][1]): i[1] for i in zip(pk_lists, keywords)}

    return dic


def texts_from_soup(soup):
    """
    soup 객체에서 성경 구절 텍스트 제너레이터 컴프리헨션을 생성한다
    :param soup: soup 객체
    :return: 성경 구절과 절 번호가 튜플로 엮인 제너레이터
    """
    contents = soup.select_one('#container > .type3 > #scrapSend > #font_chg > tbody')

    raw_paragraphs = contents.find_all('td', attrs={'class': 'num_color'})
    strip_paragraphs = (p.text.strip() for p in raw_paragraphs)

    raw_texts = contents.find_all('td', attrs={'class': 'tt'})
    strip_texts = (i.text.strip() for i in raw_texts)

    return ((item[0], item[1]) for item in zip(strip_paragraphs, strip_texts))


def make_namedtuple(dic, gen):
    """
    list에 복음서와 구절을 입혀 네임드튜플로 저장한다
    :param dic: 성경 각 권의 고유 번호와 키워드가 담긴 딕셔너리
    :param gen: 성경 구절과 절 번호 제너레이터
    :return: 성경 각 권의 키워드, 넘버, 구절이 담긴 네임드튜플
    """
    iters = ([dic[PAYLOAD['n']], PAYLOAD['p'], item[0], item[1]] for item in gen)

    return [BibleInfo(
        gospels=i[0],
        chapters=i[1],
        paragraphs=i[2],
        contents=i[3],
    ) for i in iters]


if __name__ == '__main__':
    r = requests_from_catholic_goodnews(BASE_URL, PAYLOAD)
    # print(r)
    s = soup_from_requests(r)
    # print(s)
    dic = primary_key_of_gospel(s)
    # print(dic)
    gen = texts_from_soup(s)
    # print(gen)
    n = make_namedtuple(dic, gen)
    print(n)
