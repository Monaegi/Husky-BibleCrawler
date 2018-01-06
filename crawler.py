from typing import NamedTuple
from urllib.parse import parse_qsl

import re
from bs4 import BeautifulSoup
import requests


# --- 자료구조 --- #

class BibleInfo(NamedTuple):
    """
    말씀 정보를 저장하기 위한 네임드튜플
    """
    books_name: str  # 성경책
    chapter_num: int  # 장
    paragraph_num: int  # 절
    texts: str  # 본문


# --- HTML 문서 가져오기 --- #

def make_payload(bible_num, book_num=None, chapter_num=None, commit=False):
    """
    조건에 따라 payload 값을 변경하기 위한 함수
    :param bible_num: 구약성경 / 신약성경
    :param book_num: 성경책 고유 pk
    :param chapter_num: 장 넘버
    :param commit: 책 / 장 숫자가 정해졌는가 정해지지 않았는가
    :return: payload 값이 담긴 딕셔너리
    """
    return {'m': bible_num} if commit is False else {'m': bible_num,
                                                     'n': book_num,
                                                     'p': chapter_num}


def requests_from_catholic_goodnews(payload):
    """
    payload 값을 받아 requests 객체를 반환한다
    :param payload: URL의 param 값이 담긴 payload 딕셔너리
    :return: requests 객체
    """
    # URL 변수들
    base_url = 'http://maria.catholic.or.kr/bible/read/bible_'
    url_list = 'list.asp'
    url_read = 'read.asp'

    # payload가 성경 값만 담고 있으면 list를, 책과 장 값까지 담고 있으면 read를 반환한다
    result_url = base_url + url_list if len(payload) is 1 else base_url + url_read

    # requests를 이용해 HTML 문서가 담긴 requests 객체를 받아온다
    return requests.get(result_url, params=payload)


def soup_from_requests(requests_obj):
    """
    리퀘스트 객체에서 soup 객체를 받아온다
    :param requests_obj: requests 객체
    :return: soup 객체
    """
    # requests  객체에 text 메소드를 써서 문자열 형태의 HTML 페이지를 꺼낸다
    text = requests_obj.text
    # HTML 문서를 beautifulsoup으로 렌더링해서 soup 객체로 만든다
    return BeautifulSoup(text, 'lxml')


# --- 성경 정보를 결정하기 위한 데이터 크롤링 --- #

def contents_from_soup(soup, bible_num):
    """
    soup 객체에서 성경책 이름과 링크가 담긴 tr 리스트를 꺼내고
    구약성경, 신약성경에 따라 다른 인덱스를 제거한다
    :param soup: soup 객체
    :param bible_num:
    :return: tr 리스트
    """
    # soup 객체에서 성경책 이름과 링크가 담긴 tr 리스트를 꺼낸다
    contents = soup.select('#scrapSend > .register01 > tbody > tr')

    # 구약성경이냐 신약성경이냐에 따라 다르게 퍼져 있는 제목 정보를 지운다
    if bible_num is 1:
        del contents[0], contents[5], contents[21], contents[28]
    else:
        del contents[0], contents[4], contents[5], contents[26]

    return contents


def book_info_from_contents(contents):
    """
    tr 리스트에서 href 요소가 있는 anchor 요소만 꺼낸다
    :param contents: soup 객체로부터 가공을 마친 tr 리스트
    :return: href 요소가 있는 anchor 리스트
    """

    # href 요소가 있는 td만 꺼내기 위한 함수
    def has_href(href):
        return href

    # contents에서 href만 꺼낸 뒤 우리가 가공할 한 가지 anchor만 추출한다
    # 여러 번 호출되기 때문에 제너레이터가 아닌 리스트 컴프리헨션으로 만든다
    # ex: <a href="bible_read.asp?m=1&amp;n=101&amp;p=1">창세</a>
    return [book.find_all(href=has_href)[1] for book in contents]


def names_from_book_info(book_info):
    """
    book_info 리스트에서 성경책 이름들을 꺼낸다
    :param book_info:
    :return: 성경책 이름이 담긴 제너레이터 컴프리헨션
    """
    # book_info에서 성경책 제목만 꺼낸다
    # ex: 창세, 탈출, 레위 ...
    return (name.text for name in book_info)


def pks_from_book_info(book_info):
    """
    book_info 리스트에서 성경책 고유 pk를 꺼낸다
    :param book_info:
    :return: 성경책 pk가 담긴 제너레이터 컴프리헨션
    """
    # anchor 리스트에서 href로 참조되는 URL을 꺼낸다
    # ex: /bible/read/bible_read.asp?m=2&n=101&p=1
    links = (link.get('href') for link in book_info)
    # URL을 각 요소로 분할한다
    # ex: [('/bible/read/bible_read.asp?m', '2'), ('n', '101'), ('p', '1')]
    parse = (parse_qsl(tag) for tag in links)
    # 분할한 요소 가운데 각 성경책의 고유 번호를 담고 있는 1번의 1번 튜플만 꺼낸다
    # ex: 101, 102, 103 ...
    return (pk[1][1] for pk in parse)


def chapters_from_contents(contents):
    """
    tr 리스트에서 각 성경책이 몇 장을 가지고 있는지를 꺼내온다
    :param contents: tr 리스트
    :return: 성경책의 장 수를 담고 있는 리스트
    """
    # 각 성경책이 몇 개의 장을 가지고 있는지를 가져온다
    chapter_lists = []
    for chapter in contents:
        # 정규표현식으로 <td> 요소들 가운데서 '총 00장' 문구만 꺼낸다
        raw_td = chapter.find(string=re.compile(r'^\w\s\d+\w$'))
        # '총 00장' 문구에서 숫자만 걸러낸다
        chapter_num = re.search(r'\d+', raw_td)
        # 숫자를 미리 정의한 리스트에 추가한다
        chapter_lists.append(chapter_num.group())

    return chapter_lists


# --- 성경 정보가 결정된 이후 성경 본문 크롤링 --- #

def texts_from_soup(soup):
    """
    soup 객체에서 성경 구절 제너레이터 컴프리헨션을 생성한다
    :param soup: soup 객체
    :return: 성경 절과 본문이 튜플로 엮인 제너레이터
    """
    # soup 객체에서 성경 절과 본문이 함께 담긴 <tbody>요소를 꺼낸다
    contents = soup.select_one('#container > .type3 > #scrapSend > #font_chg > tbody')

    # <tbody> 요소에서 성경 절 정보가 담긴 <td> 요소를 리스트로 꺼낸다
    raw_paragraphs = contents.find_all('td', attrs={'class': 'num_color'})
    # <td> 요소에서 순수 숫자만 꺼낸다
    # ex: 1, 2, 3, 4, ...
    strip_paragraphs = (pg.text.strip() for pg in raw_paragraphs)

    # <tbody> 요소에서 성경 본문 정보가 담긴 <td> 요소를 리스트로 꺼낸다
    raw_texts = contents.find_all('td', attrs={'class': 'tt'})
    # <td> 요소에서 순수 텍스트만 꺼낸다
    # ex: 다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보. ...
    strip_texts = (i.text.strip() for i in raw_texts)

    # strip_paragraphs와 strip_texts를 병렬 순회하여 두 요소를 튜플로 담은 제너레이터를 만든다
    # ex: ('1', '다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보.') ...
    raw_gen = ((item[0], item[1]) for item in zip(strip_paragraphs, strip_texts))

    # 본문이 아닌 제목 요소를 제거하기 위해 조건문을 달아 순회한다
    return (i for i in raw_gen if i[0] is not '')


def make_namedtuple(payload, dic, gen):
    """
    list에 복음서와 구절을 입혀 네임드튜플로 저장한다
    :param payload: URL param 값
    :param dic: 성경 각 권의 고유 번호와 키워드가 담긴 딕셔너리
    :param gen: 성경 구절과 절 번호 제너레이터
    :return: 성경 각 권의 키워드, 넘버, 구절이 담긴 네임드튜플
    """
    # BibleInfo 네임드튜플에 담기 위해 딕셔너리와 제너레이터를 병렬 순회하여 모든 요소를 하나의 리스트에 담은 제너레이터를 만든다
    # ex: ['마태', 1, '1', '다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보.'] ...

    # 제너레이터를 리스트 컴프리헨션으로 순회하며 네임드튜플에 담는다
    # ex: BibleInfo(books='마태', chapters=1, paragraphs=1, contents='다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보.') ...


if __name__ == '__main__':
    # 책과 장이 결정되기 전까지
    d = make_payload(1)
    p = make_payload(1, 101, 1, commit=True)
    r = requests_from_catholic_goodnews(d)
    s = soup_from_requests(r)
