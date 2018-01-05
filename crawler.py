from typing import NamedTuple
from urllib.parse import parse_qsl

from bs4 import BeautifulSoup
import requests


class BibleInfo(NamedTuple):
    """
    말씀 정보를 저장하기 위한 네임드튜플
    """
    gospels: str  # 성경책
    chapters: int  # 장
    paragraphs: str  # 절
    contents: str  # 본문


def make_payload(bible_num, book_num=None, paragraph_num=None, commit=False):
    """
    조건에 따라 payload 값을 변경하기 위한 함수
    :param bible_num: 구약성경 / 신약성경
    :param book_num: 성경책 고유 pk
    :param paragraph_num: 장 넘버
    :param commit: 책 / 장 숫자가 정해졌는가 정해지지 않았는가
    :return: payload 값이 담긴 딕셔너리
    """
    return {'m': bible_num} if commit is False else {'m': bible_num,
                                                     'n': book_num,
                                                     'p': paragraph_num}


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


def primary_key_of_gospel(soup):
    """
    soup 객체에서 성경책 이름과 고유 번호를 가져와 Dict를 생성한다
    :param soup: soup 객체
    :return: 성경책 이름과 고유 번호의 Dict
    """
    # soup 객체에서 성경책 이름과 링크가 담긴 anchor 리스트를 꺼낸다
    # ex: <a href="/bible/read/bible_read.asp?m=2&amp;n=101&amp;p=1">창세</a>
    contents = soup.select('#container > .list_c2 > li > .list_c2_sub > li > a')

    # anchor 리스트에서 href로 참조되는 URL을 꺼낸다
    # ex: /bible/read/bible_read.asp?m=2&n=101&p=1
    links = (i.get('href') for i in contents)
    # URL을 각 요소로 분할한다
    # ex: [('/bible/read/bible_read.asp?m', '2'), ('n', '101'), ('p', '1')]
    parse = (parse_qsl(i) for i in links)
    # 분할한 요소 가운데 각 성경책의 고유 번호를 담고 있는 1번 튜플만 꺼낸다
    # ex: ('n', '101')
    pk_lists = (i[1] for i in parse)

    # anchor 리스트에서 순수 텍스트만 꺼낸다
    # ex: '창세'
    keywords = (i.get_text() for i in contents)

    # pk_lists와 keywords를 병렬 순회하여 두 요소를 담은 딕셔너리를 만든다
    # ex: {101: '창세', 102: '탈출', 103: '레위', 104: '민수' ...}
    return {int(i[0][1]): i[1] for i in zip(pk_lists, keywords)}


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
    strip_paragraphs = (p.text.strip() for p in raw_paragraphs)

    # <tbody> 요소에서 성경 본문 정보가 담긴 <td> 요소를 리스트로 꺼낸다
    raw_texts = contents.find_all('td', attrs={'class': 'tt'})
    # <td> 요소에서 순수 텍스트만 꺼낸다
    # ex: 다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보. ...
    strip_texts = (i.text.strip() for i in raw_texts)

    # strip_paragraphs와 strip_texts를 병렬 순회하여 두 요소를 튜플로 담은 제너레이터를 만든다
    # ex: ('1', '다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보.') ...
    return ((item[0], item[1]) for item in zip(strip_paragraphs, strip_texts))


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
    result_comp = ([dic[payload['n']], payload['p'], item[0], item[1]] for item in gen)

    # 제너레이터를 리스트 컴프리헨션으로 순회하며 네임드튜플에 담는다
    # ex: BibleInfo(gospels='마태', chapters=1, paragraphs='1', contents='다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보.') ...
    return [BibleInfo(
        gospels=i[0],
        chapters=i[1],
        paragraphs=i[2],
        contents=i[3],
    ) for i in result_comp]


if __name__ == '__main__':
    # 책과 장이 결정되기 전까지
    d = make_payload(1)
    p = make_payload(1, 101, 1, commit=True)
    r = requests_from_catholic_goodnews(p)
    s = soup_from_requests(r)

    # 책과 장이 결정되어야 가능함
    g = primary_key_of_gospel(s)
    t = texts_from_soup(s)
    m = make_namedtuple(p, g, t)
    print(m)
