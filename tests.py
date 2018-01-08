import unittest
from unittest.mock import patch

from crawler import BibleCrawler
import main


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        """
        크롤러 테스트를 위한 전역변수 설정
        :return: None
        """
        self.crawler = BibleCrawler()

    # --- HTML 문서 가져오기 --- #

    def test_make_payload(self):
        """
        payload 값을 결정하는 함수가 조건에 따라 다르게 작동하는지 테스트
        :return: None
        """
        payload_old = self.crawler.make_payload(1)
        self.assertEqual(len(payload_old), 1)

        payload_new = self.crawler.make_payload(2)
        self.assertEqual(len(payload_new), 1)

        payload_item = self.crawler.make_payload(1, 101, 1, commit=True)
        self.assertEqual(len(payload_item), 3)

    def test_requests_from_catholic_goodnews(self):
        """
        Request 객체가 정상적으로 생성되어 200 응답코드를 주는지 테스트
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        self.assertEqual(requests_old.status_code, 200)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        self.assertEqual(requests_new.status_code, 200)

        params_item = self.crawler.make_payload(1, 101, 1, commit=True)
        requests_item = self.crawler.requests_from_catholic_goodnews(params_item)
        self.assertEqual(requests_item.status_code, 200)

    def test_soup_is_exist(self):
        """
        BeautifulSoup 객체가 정상적으로 생성되는지 테스트
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        self.assertFalse(soup_old.can_be_empty_element)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        soup_new = self.crawler.soup_from_requests(requests_new)
        self.assertFalse(soup_new.can_be_empty_element)

        params_item = self.crawler.make_payload(1, 101, 1, commit=True)
        requests_item = self.crawler.requests_from_catholic_goodnews(params_item)
        soup_item = self.crawler.soup_from_requests(requests_item)
        self.assertFalse(soup_item.can_be_empty_element)

    # --- 성경 정보를 결정하기 위한 데이터 크롤링 --- #

    def test_list_contents_from_soup(self):
        """
        soup 객체에서 가져온 contents 객체가 구약성경, 신약성경에 따라 필요없는 요소를 잘 제거하는가
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        list_contents_old = self.crawler.list_contents_from_soup(soup_old, 1)
        self.assertEqual(len(list_contents_old), 46)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        soup_new = self.crawler.soup_from_requests(requests_new)
        list_contents_new = self.crawler.list_contents_from_soup(soup_new, 2)
        self.assertEqual(len(list_contents_new), 27)

    def test_book_info_from_list_contents(self):
        """
        contents 객체로부터 book_info 리스트가 잘 생성되는지 테스트
        :return:
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        list_contents_old = self.crawler.list_contents_from_soup(soup_old, 1)
        book_info_old = self.crawler.book_info_from_list_contents(list_contents_old)
        self.assertEqual(len(book_info_old), 46)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        soup_new = self.crawler.soup_from_requests(requests_new)
        list_contents_new = self.crawler.list_contents_from_soup(soup_new, 2)
        book_info_new = self.crawler.book_info_from_list_contents(list_contents_new)
        self.assertEqual(len(book_info_new), 27)

    def test_pks_from_book_list(self):
        """
        book_info 리스트에서 pk 리스트를 잘 가져오는지 테스트
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        list_contents_old = self.crawler.list_contents_from_soup(soup_old, 1)
        book_info_old = self.crawler.book_info_from_list_contents(list_contents_old)
        pks_old = self.crawler.pks_from_book_info(book_info_old)
        li = [i for i in pks_old]
        self.assertEqual(len(li), 46)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        soup_new = self.crawler.soup_from_requests(requests_new)
        list_contents_new = self.crawler.list_contents_from_soup(soup_new, 2)
        book_info_new = self.crawler.book_info_from_list_contents(list_contents_new)
        pks_new = self.crawler.pks_from_book_info(book_info_new)
        li = [i for i in pks_new]
        self.assertEqual(len(li), 27)

    def test_names_from_book_info(self):
        """
        book_info 리스트에서 성경책 이름을 잘 가져오는지 테스트
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        list_contents_old = self.crawler.list_contents_from_soup(soup_old, 1)
        book_info_old = self.crawler.book_info_from_list_contents(list_contents_old)
        names_old = self.crawler.names_from_book_info(book_info_old)
        li = [i for i in names_old]
        self.assertEqual(len(li), 46)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        soup_new = self.crawler.soup_from_requests(requests_new)
        list_contents_new = self.crawler.list_contents_from_soup(soup_new, 2)
        book_info_new = self.crawler.book_info_from_list_contents(list_contents_new)
        names_new = self.crawler.names_from_book_info(book_info_new)
        li = [i for i in names_new]
        self.assertEqual(len(li), 27)

    def test_chapters_from_list_contents(self):
        """
        contents 리스트에서 chapter 리스트를 잘 가져오는지 테스트
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        list_contents_old = self.crawler.list_contents_from_soup(soup_old, 1)
        chapters_old = self.crawler.chapters_from_list_contents(list_contents_old)
        self.assertEqual(len(chapters_old), 46)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        soup_new = self.crawler.soup_from_requests(requests_new)
        list_contents_new = self.crawler.list_contents_from_soup(soup_new, 2)
        chapters_new = self.crawler.book_info_from_list_contents(list_contents_new)
        self.assertEqual(len(chapters_new), 27)

    def test_namedtuple_from_bible_data(self):
        """
        성경 데이터를 수합하는 네임드튜플 만들기 함수가 잘 작동하는지 테스트
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        list_contents_old = self.crawler.list_contents_from_soup(soup_old, 1)
        book_info_old = self.crawler.book_info_from_list_contents(list_contents_old)
        pks_old = self.crawler.pks_from_book_info(book_info_old)
        names_old = self.crawler.names_from_book_info(book_info_old)
        chapters_old = self.crawler.chapters_from_list_contents(list_contents_old)
        bible_data_old = self.crawler.make_bible_data(pks_old, names_old, chapters_old)
        self.assertEqual(len(bible_data_old), 46)

        params_new = self.crawler.make_payload(2)
        requests_new = self.crawler.requests_from_catholic_goodnews(params_new)
        soup_new = self.crawler.soup_from_requests(requests_new)
        list_contents_new = self.crawler.list_contents_from_soup(soup_new, 2)
        book_info_new = self.crawler.book_info_from_list_contents(list_contents_new)
        pks_new = self.crawler.pks_from_book_info(book_info_new)
        names_new = self.crawler.names_from_book_info(book_info_new)
        chapters_new = self.crawler.book_info_from_list_contents(list_contents_new)
        bible_data_new = self.crawler.make_bible_data(pks_new, names_new, chapters_new)
        self.assertEqual(len(bible_data_new), 27)

    # --- 성경 정보가 결정된 이후 본문 크롤링 --- #

    def test_read_contents_is_exist(self):
        """
        soup 객체에서 본문과 절 정보가 담긴 <tbody> 요소를 잘 가져오는지 테스트
        :return: None
        """
        params_item = self.crawler.make_payload(1, 101, 1, commit=True)
        requests_item = self.crawler.requests_from_catholic_goodnews(params_item)
        soup_item = self.crawler.soup_from_requests(requests_item)
        read_contents = self.crawler.read_contents_from_soup(soup_item)
        self.assertFalse(read_contents.can_be_empty_element)

    def test_paragraphs_from_read_contents(self):
        """
        read_contents에서 성경 절 정보를 잘 가져오는지 테스트
        :return: None
        """
        params_item = self.crawler.make_payload(1, 101, 1, commit=True)
        requests_item = self.crawler.requests_from_catholic_goodnews(params_item)
        soup_item = self.crawler.soup_from_requests(requests_item)
        read_contents = self.crawler.read_contents_from_soup(soup_item)
        paragraphs = self.crawler.paragraphs_from_read_contents(read_contents)
        self.assertIsNotNone(paragraphs)

    def test_texts_from_read_contents(self):
        """
        read_contents에서 성경 본문 정보를 잘 가져오는지 테스트
        :return: None
        """
        params_item = self.crawler.make_payload(1, 101, 1, commit=True)
        requests_item = self.crawler.requests_from_catholic_goodnews(params_item)
        soup_item = self.crawler.soup_from_requests(requests_item)
        read_contents = self.crawler.read_contents_from_soup(soup_item)
        texts = self.crawler.texts_from_read_contents(read_contents)
        self.assertIsNotNone(texts)

    def test_namedtuple_from_bible_info(self):
        """
        모든 요소들이 네임드튜플로 생성되는지 테스트
        :return: None
        """
        params_old = self.crawler.make_payload(1)
        requests_old = self.crawler.requests_from_catholic_goodnews(params_old)
        soup_old = self.crawler.soup_from_requests(requests_old)
        list_contents_old = self.crawler.list_contents_from_soup(soup_old, 1)
        book_info_old = self.crawler.book_info_from_list_contents(list_contents_old)
        pks_old = self.crawler.pks_from_book_info(book_info_old)
        names_old = self.crawler.names_from_book_info(book_info_old)
        chapters_old = self.crawler.chapters_from_list_contents(list_contents_old)
        bible_data_old = self.crawler.make_bible_data(pks_old, names_old, chapters_old)

        params_item = self.crawler.make_payload(1, 101, 1, commit=True)
        requests_item = self.crawler.requests_from_catholic_goodnews(params_item)
        soup_item = self.crawler.soup_from_requests(requests_item)
        read_contents = self.crawler.read_contents_from_soup(soup_item)
        paragraphs = self.crawler.paragraphs_from_read_contents(read_contents)
        texts = self.crawler.texts_from_read_contents(read_contents)

        bible_data = bible_data_old[101]
        bible_info = self.crawler.make_bible_info(bible_data, (1, 101, 1), paragraphs, texts)
        self.assertEqual(len(bible_info), 31)


class UITest(unittest.TestCase):
    def setUp(self):
        """
        UI 테스트를 위한 전역변수 설정
        1. self.elements: main.py의 Elements 클래스
        :return:
        """
        self.elements = main.Elements()

    def test_elements(self):
        """
        UI 요소가 잘 출력되는지 테스트
        :return:
        """
        bar = self.elements.main_bar
        self.assertEqual(len(bar), 52)
        title = self.elements.main_title
        self.assertEqual(title.replace(' ', ''), "가톨릭말씀사탕")

    def test_get_input_quit_message_from_start_menu(self):
        """
        input 함수에서 'q' 메시지를 넣었을 때 잘 종료되는지 테스트
        :return:
        """
        user_input = [
            'q',
        ]
        expected_stacks = [
            self.elements.validate('q'),
        ]
        with patch('builtins.input', side_effect=user_input):
            stacks = self.elements.start_menu()
        self.assertEqual(stacks, expected_stacks[0])

    # def test_get_gospel_message(self):
    #     """
    #     말씀을 잘 가져오는지 테스트
    #     :return:
    #     """
    #     message = self.elements.get_message()
    #     self.assertIsNotNone(message)


if __name__ == '__main__':
    unittest.main()
