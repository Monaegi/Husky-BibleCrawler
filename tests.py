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
        self.params_without_item = crawler.make_payload(1)
        self.requests_1 = crawler.requests_from_catholic_goodnews(self.params_without_item)
        self.soup_1 = crawler.soup_from_requests(self.requests_1)

        self.params_with_extra_item = crawler.make_payload(
            bible_num=1,
            book_num=101,
            chapter_num=1,
            commit=True
        )
        self.requests_2 = crawler.requests_from_catholic_goodnews(payload=self.params_with_extra_item)
        self.soup_2 = crawler.soup_from_requests(self.requests_2)

        self.dict = crawler.primary_key_of_gospel(self.soup_2)
        self.generator = crawler.texts_from_soup(self.soup_2)
        self.namedtuple = crawler.make_namedtuple(self.params_with_extra_item, self.dict, self.generator)

    def test_make_payload(self):
        """
        payload 값을 결정하는 함수가 조건에 따라 다르게 작동하는지 테스트
        :return: None
        """
        payload_default = crawler.make_payload(bible_num=1, commit=False)
        self.assertEqual(len(payload_default), 1)
        payload_after_decision = crawler.make_payload(
            bible_num=1,
            book_num=101,
            chapter_num=1,
            commit=True)
        self.assertEqual(len(payload_after_decision), 3)

    def test_requests_from_catholic_goodnews(self):
        """
        Request 객체가 정상적으로 생성되어 200 응답코드를 주는지 테스트
        :return: None
        """
        requests = self.requests_2
        self.assertEqual(requests.status_code, 200)

    def test_soup_is_exist(self):
        """
        BeautifulSoup 객체가 정상적으로 생성되는지 테스트
        :return: None
        """
        soup = self.soup_2
        self.assertFalse(soup.can_be_empty_element)

    def test_book_list(self):
        """
        성경책 리스트 크롤링 테스트
        :return:
        """
        dic = crawler.book_list_from_soup(self.soup_1)
        self.assertEqual(len(dic), 46)

    def test_select_primary_key_of_gospel(self):
        """
        복음서의 pk값과 성경책 이름을 Dict로 크롤링한 것이 정상적으로 생성되는지 테스트
        :return: None
        """
        dic = self.dict
        self.assertEqual(len(dic), 246)

    def test_select_texts_from_soup(self):
        """
        BS 객체에서 뽑아낸 성경 구절 튜플이 정상적으로 생성되는지 테스트
        :return: None
        """
        gen = self.generator
        li = [i for i in gen]
        self.assertIsNotNone(li)

    def test_namedtuple_from_list(self):
        """
        모든 요소들이 네임드튜플로 생성되는지 테스트
        :return: None
        """
        namedtuple = self.namedtuple
        self.assertIsNotNone(namedtuple)


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
