import unittest
from unittest.mock import patch

import crawler
import main


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        """
        크롤러 테스트를 위한 전역변수 설정
        :return: None
        """
        # payload 설정
        self.params_old = crawler.make_payload(1)
        self.params_new = crawler.make_payload(2)
        self.params_item = crawler.make_payload(1, 101, 1, commit=True)

        # 구약성경 설정
        self.requests_old = crawler.requests_from_catholic_goodnews(self.params_old)
        self.soup_old = crawler.soup_from_requests(self.requests_old)
        self.list_contents_old = crawler.list_contents_from_soup(self.soup_old, 1)
        self.book_info_old = crawler.book_info_from_list_contents(self.list_contents_old)
        self.names_old = crawler.names_from_book_info(self.book_info_old)
        self.pks_old = crawler.pks_from_book_info(self.book_info_old)
        self.chapters_old = crawler.chapters_from_list_contents(self.list_contents_old)

        # 신약성경 설정
        self.requests_new = crawler.requests_from_catholic_goodnews(self.params_new)
        self.soup_new = crawler.soup_from_requests(self.requests_new)
        self.list_contents_new = crawler.list_contents_from_soup(self.soup_new, 2)
        self.book_info_new = crawler.book_info_from_list_contents(self.list_contents_new)
        self.names_new = crawler.names_from_book_info(self.book_info_new)
        self.pks_new = crawler.pks_from_book_info(self.book_info_new)
        self.chapters_new = crawler.chapters_from_list_contents(self.list_contents_new)

        # 본문 설정
        self.requests_item = crawler.requests_from_catholic_goodnews(self.params_item)
        self.soup_item = crawler.soup_from_requests(self.requests_item)
        self.read_contents = crawler.read_contents_from_soup(self.soup_item)

    # --- HTML 문서 가져오기 --- #

    def test_make_payload(self):
        """
        payload 값을 결정하는 함수가 조건에 따라 다르게 작동하는지 테스트
        :return: None
        """
        payload_old = self.params_old
        self.assertEqual(len(payload_old), 1)

        payload_new = self.params_new
        self.assertEqual(len(payload_new), 1)

        payload_item = self.params_item
        self.assertEqual(len(payload_item), 3)

    def test_requests_from_catholic_goodnews(self):
        """
        Request 객체가 정상적으로 생성되어 200 응답코드를 주는지 테스트
        :return: None
        """
        requests_old = self.requests_old
        self.assertEqual(requests_old.status_code, 200)

        requests_new = self.requests_new
        self.assertEqual(requests_new.status_code, 200)

    def test_soup_is_exist(self):
        """
        BeautifulSoup 객체가 정상적으로 생성되는지 테스트
        :return: None
        """
        soup_old = self.soup_old
        self.assertFalse(soup_old.can_be_empty_element)

        soup_new = self.soup_new
        self.assertFalse(soup_new.can_be_empty_element)

    # --- 성경 정보를 결정하기 위한 데이터 크롤링 --- #

    def test_contents_from_soup(self):
        """
        soup 객체에서 가져온 contents 객체가 구약성경, 신약성경에 따라 필요없는 요소를 잘 제거하는가
        :return: None
        """
        list_contents_old = self.list_contents_old
        self.assertEqual(len(list_contents_old), 46)

        list_contents_new = self.list_contents_new
        self.assertEqual(len(list_contents_new), 27)

    def test_book_info_from_list_contents(self):
        """
        contents 객체로부터 book_info 리스트가 잘 생성되는지 테스트
        :return:
        """
        book_info_old = self.book_info_old
        self.assertEqual(len(book_info_old), 46)

        book_info_new = self.book_info_new
        self.assertEqual(len(book_info_new), 27)

    def test_pks_from_book_list(self):
        """
        book_info 리스트에서 pk 리스트를 잘 가져오는지 테스트
        :return: None
        """
        pks_old = self.pks_old
        li = [i for i in pks_old]
        self.assertEqual(len(li), 46)

        pks_new = self.pks_new
        li = [i for i in pks_new]
        self.assertEqual(len(li), 27)

    def test_names_from_book_info(self):
        """
        book_info 리스트에서 성경책 이름을 잘 가져오는지 테스트
        :return: None
        """
        names_old = self.names_old
        li = [i for i in names_old]
        self.assertEqual(len(li), 46)

        names_new = self.names_new
        li = [i for i in names_new]
        self.assertEqual(len(li), 27)

    def test_chapters_from_list_contents(self):
        """
        contents 리스트에서 chapter 리스트를 잘 가져오는지 테스트
        :return: None
        """
        chapters_old = self.chapters_old
        self.assertEqual(len(chapters_old), 46)

        chapters_new = self.chapters_new
        self.assertEqual(len(chapters_new), 27)

    def test_namedtuple_from_bible_data(self):
        """
        성경 데이터를 수합하는 네임드튜플 만들기 함수가 잘 작동하는지 테스트
        :return: None
        """
        bible_data_old = crawler.make_bible_data(self.pks_old, self.names_old, self.chapters_old)
        self.assertEqual(len(bible_data_old), 46)

        bible_data_new = crawler.make_bible_data(self.pks_new, self.names_new, self.chapters_new)
        self.assertEqual(len(bible_data_new), 27)

    # --- 성경 정보가 결정된 이후 본문 크롤링 --- #

    def test_read_contents_is_exist(self):
        """
        soup 객체에서 본문과 절 정보가 담긴 <tbody> 요소를 잘 가져오는지 테스트
        :return: None
        """
        read_contents = self.read_contents
        self.assertFalse(read_contents.can_be_empty_element)

    def test_paragraphs_from_read_contents(self):
        """
        read_contents에서 성경 절 정보를 잘 가져오는지 테스트
        :return: None
        """
        paragraphs = crawler.paragraphs_from_read_contents(self.read_contents)
        self.assertIsNotNone(paragraphs)

    def test_texts_from_read_contents(self):
        """
        read_contents에서 성경 본문 정보를 잘 가져오는지 테스트
        :return: None
        """
        texts = crawler.texts_from_read_contents(self.read_contents)
        self.assertIsNotNone(texts)

    def test_namedtuple_from_list(self):
        """
        모든 요소들이 네임드튜플로 생성되는지 테스트
        :return: None
        """


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

    def test_get_gospel_message(self):
        """
        말씀을 잘 가져오는지 테스트
        :return:
        """
        message = self.elements.get_message()
        self.assertIsNotNone(message)


if __name__ == '__main__':
    unittest.main()
