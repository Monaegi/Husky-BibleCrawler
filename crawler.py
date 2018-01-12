import sqlite3
from typing import NamedTuple
from urllib.parse import parse_qsl

import re
from bs4 import BeautifulSoup
import requests


# --- 자료구조 --- #

class BibleData(NamedTuple):
    """
    성경 데이터를 정의하는 네임드튜플
    """
    books_name: str  # 성경책
    chapters_count: int  # 각 성경책이 보유한 장 수


class BibleInfo(NamedTuple):
    """
    본문 정보를 저장하기 위한 네임드튜플
    """
    books_name: str  # 성경책
    chapter_num: int  # 장
    paragraph_num: str  # 절
    texts: str  # 본문


# --- 크롤러 --- #

class BibleCrawler:
    """
    <가톨릭 굿뉴스>의 성경 구절을 무작위로 가져오는 크롤러
    """

    def __init__(self):
        """
        인스턴스 속성 정의
        """
        self.__commit = False
        self.__bible_num = None
        self.__primary_key = None
        self.__chapter_num = None
        self.__bible_data = None

    # --- 네임 맹글링 --- #

    @property
    def commit(self):
        return self.__commit

    @commit.setter
    def commit(self, input_bool):
        self.__commit = input_bool

    @property
    def bible_num(self):
        return self.__bible_num

    @bible_num.setter
    def bible_num(self, input_num):
        self.__bible_num = input_num

    @property
    def primary_key(self):
        return self.__primary_key

    @primary_key.setter
    def primary_key(self, input_key):
        self.__primary_key = input_key

    @property
    def chapter_num(self):
        return self.__chapter_num

    @chapter_num.setter
    def chapter_num(self, input_num):
        self.__chapter_num = input_num

    @property
    def bible_data(self):
        return self.__bible_data

    @bible_data.setter
    def bible_data(self, input_data):
        self.__bible_data = input_data

    # --- HTML 문서 가져오기 --- #

    def make_payload(self):
        """
        조건에 따라 payload 값을 변경하기 위한 함수
        :return: payload 값이 담긴 딕셔너리
        """
        return {'m': self.bible_num} \
            if self.commit is False else {'m': self.bible_num,
                                          'n': self.primary_key,
                                          'p': self.chapter_num}

    def requests_from_catholic_goodnews(self):
        """
        payload 값을 받아 requests 객체를 반환한다
        :return: requests 객체
        """
        # self.payload를 사용하되 만일 비어 있다면 메서드를 호출한다
        payload = self.make_payload()

        # URL 변수들
        base_url = 'http://maria.catholic.or.kr/bible/read/bible_'
        url_list = 'list.asp'
        url_read = 'read.asp'

        # payload가 성경 값만 담고 있으면 list를, 책과 장 값까지 담고 있으면 read를 반환한다
        result_url = base_url + url_list if len(payload) is 1 else base_url + url_read

        # requests를 이용해 HTML 문서가 담긴 requests 객체를 받아온다
        return requests.get(result_url, params=payload)

    def soup_from_requests(self):
        """
        리퀘스트 객체에서 soup 객체를 받아온다
        :return: soup 객체
        """
        # self.requests_obj를 사용하되 만일 비어 있다면 메서드를 호출한다
        requests_obj = self.requests_from_catholic_goodnews()

        # requests  객체에 text 메소드를 써서 문자열 형태의 HTML 페이지를 꺼낸다
        text = requests_obj.text
        # HTML 문서를 beautifulsoup으로 렌더링해서 soup 객체로 만든다
        return BeautifulSoup(text, 'lxml')

    # --- 성경 정보를 결정하기 위한 데이터 크롤링 --- #

    def list_contents_from_soup(self):
        """
        soup 객체에서 성경책 이름과 링크가 담긴 tr 리스트를 꺼내고
        구약성경, 신약성경에 따라 다른 인덱스를 제거한다
        :return: tr 리스트
        """
        # self.soup을 사용하되 만일 비어 있다면 메서드를 호출한다
        soup = self.soup_from_requests()

        # soup 객체에서 성경책 이름과 링크가 담긴 tr 리스트를 꺼낸다
        contents = soup.select('#scrapSend > .register01 > tbody > tr')

        # 구약성경이냐 신약성경이냐에 따라 다르게 퍼져 있는 제목 정보를 지운다
        if self.bible_num is 1:
            del contents[0], contents[5], contents[21], contents[28]
        else:
            del contents[0], contents[4], contents[5], contents[26]

        return contents

    def book_info_from_list_contents(self):
        """
        tr 리스트에서 href 요소가 있는 anchor 요소만 꺼낸다
        :return: href 요소가 있는 anchor 리스트
        """
        # self.list_contents를 사용하되 만일 비어 있다면 메서드를 호출한다
        list_contents = self.list_contents_from_soup()

        # href 요소가 있는 td만 꺼내기 위한 함수
        def has_href(href):
            return href

        # contents에서 href만 꺼낸 뒤 우리가 가공할 한 가지 anchor만 추출한다
        # 여러 번 호출되기 때문에 제너레이터가 아닌 리스트 컴프리헨션으로 만든다
        # ex: <a href="bible_read.asp?m=1&amp;n=101&amp;p=1">창세</a>
        return [book.find_all(href=has_href)[1] for book in list_contents]

    def pks_from_book_info(self):
        """
        book_info 리스트에서 성경책 고유 pk를 꺼낸다
        :return: 성경책 pk가 담긴 제너레이터 컴프리헨션
        """
        # self.book_info를 사용하되 만일 비어 있다면 메서드를 호출한다
        book_info = self.book_info_from_list_contents()

        # anchor 리스트에서 href로 참조되는 URL을 꺼낸다
        # ex: /bible/read/bible_read.asp?m=2&n=101&p=1
        links = (link.get('href') for link in book_info)
        # URL을 각 요소로 분할한다
        # ex: [('/bible/read/bible_read.asp?m', '2'), ('n', '101'), ('p', '1')]
        parse = (parse_qsl(tag) for tag in links)
        # 분할한 요소 가운데 각 성경책의 고유 번호를 담고 있는 1번의 1번 튜플만 꺼낸다
        # ex: 101, 102, 103 ...
        return (pk[1][1] for pk in parse)

    def names_from_book_info(self):
        """
        book_info 리스트에서 성경책 이름들을 꺼낸다
        :return: 성경책 이름이 담긴 제너레이터 컴프리헨션
        """
        # self.book_info를 사용하되 만일 비어 있다면 메서드를 호출한다
        book_info = self.book_info_from_list_contents()

        # book_info에서 성경책 제목만 꺼낸다
        # ex: 창세, 탈출, 레위 ...
        return (name.text for name in book_info)

    def chapters_from_list_contents(self):
        """
        tr 리스트에서 각 성경책이 몇 장을 가지고 있는지를 꺼내온다
        :return: 성경책의 장 수를 담고 있는 리스트
        """
        # self.list_contents를 사용하되 만일 비어 있다면 메서드를 호출한다
        list_contents = self.list_contents_from_soup()

        # 각 성경책이 몇 개의 장을 가지고 있는지를 가져온다
        chapter_lists = []
        for chapter in list_contents:
            # 정규표현식으로 <td> 요소들 가운데서 '총 00장' 문구만 꺼낸다
            raw_td = chapter.find(string=re.compile(r'^\w\s\d+\w$'))
            # '총 00장' 문구에서 숫자만 걸러낸다
            chapter_num = re.search(r'\d+', raw_td)
            # 숫자를 미리 정의한 리스트에 추가한다
            chapter_lists.append(chapter_num.group())

        return chapter_lists

    def make_bible_data(self):
        """
        성경 데이터를 수합하는 네임드튜플을 만든다
        :return: 성경 pk와 이름, 장 수의 네임드튜플로 이루어진 딕셔너리
        """
        # 인스턴스 속성을 가져오거나 속성이 없다면 메서드를 호출한다
        pks = self.pks_from_book_info()
        names = self.names_from_book_info()
        chapters = self.chapters_from_list_contents()
        list_comp = ((i[0], i[1]) for i in zip(names, chapters))

        self.bible_data = {int(i[0]): BibleData(
            books_name=i[1][0],
            chapters_count=i[1][1],
        ) for i in zip(pks, list_comp)}
        return self.bible_data

    # --- 성경 정보가 결정된 이후 본문 크롤링 --- #

    def read_contents_from_soup(self):
        """
        soup 객체에서 성경 본문과 절 정보가 담긴 <tbody> 요소를 꺼낸다
        :return: 성경 본문과 절 정보가 담긴 <tbody> 요소
        """
        # self.soup을 사용하되 만일 비어 있다면 메서드를 호출한다
        soup = self.soup_from_requests()

        return soup.select_one('#container > .type3 > #scrapSend > #font_chg > tbody')

    def paragraphs_from_read_contents(self):
        """
        read contents에서 성경 절 정보를 가져온다
        :return: 성경 절 정보가 담긴 제너레이터 컴프리헨션
        """
        # self.read_contents를 사용하되 만일 비어 있다면 메서드를 호출한다
        read_contents = self.read_contents_from_soup()

        # <tbody> 요소에서 성경 절 정보가 담긴 <td> 요소를 리스트로 꺼낸다
        raw_paragraphs = read_contents.find_all('td', attrs={'class': 'num_color'})
        # <td> 요소에서 순수 숫자만 꺼낸다
        # ex: 1, 2, 3, 4, ...
        return (sp.text.strip() for sp in raw_paragraphs)

    def texts_from_read_contents(self):
        """
        read_contents에서 성경 본문 정보를 가져온다
        :return: 성경 본문 정보가 담긴 제너레이터 컴프리헨션
        """
        # self.read_contents를 사용하되 만일 비어 있다면 메서드를 호출한다
        read_contents = self.read_contents_from_soup()

        # <tbody> 요소에서 성경 본문 정보가 담긴 <td> 요소를 리스트로 꺼낸다
        raw_texts = read_contents.find_all('td', attrs={'class': 'tt'})
        # <td> 요소에서 순수 텍스트만 꺼낸다
        # ex: 다윗의 자손이시며 아브라함의 자손이신 예수 그리스도의 족보. ...
        return (i.text.strip() for i in raw_texts)

    def make_bible_info(self, conn):
        """
        본문 정보가 담긴 자료구조를 생성한다
        :return: 본문 정보 네임드튜플로 구성된 리스트
        """
        # sql 명령문: bible_data 테이블에서 입력한 primary_key 값에 해당하는 name을 출력하라
        sql_command = """ SELECT name FROM bible_data WHERE bible_pk=%d """ % self.primary_key

        # 커서를 꺼내 db를 검색한다
        cursor = conn.cursor()
        try:
            data = cursor.execute(sql_command)
            books_name = [book for book in data][0][0]

        # 예외처리: data_table이 없을 경우
        except sqlite3.Error as e:
            print(e)
            books_name = self.bible_data[self.primary_key].books_name

        # paragraphs와 texts를 호출한다
        paragraphs = self.paragraphs_from_read_contents()
        texts = self.texts_from_read_contents()

        # paragraphs와 texts를 병렬 순회하며 성경 제목이 담긴 요소를 제거한다
        strip_comp = ((i[0], i[1]) for i in zip(paragraphs, texts) if i[0] is not '')

        # 성경 제목이 제거된 제너레이터에 성경책 이름과 장 숫자를 첨가해 새로운 제너레이터를 만든다
        result_comp = ((books_name, self.chapter_num, i[0], i[1]) for i in strip_comp)

        # 최종 제너레이터를 순회하며 네임드튜플에 담는다
        return [BibleInfo(
            books_name=i[0],
            chapter_num=i[1],
            paragraph_num=i[2],
            texts=i[3],
        ) for i in result_comp]


if __name__ == '__main__':
    pass
