import unittest
from unittest.mock import patch

from crawler import BibleCrawler
from main import Main


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        """
        크롤러 테스트를 위한 전역변수 설정
        :return: None
        """
        self.crawler = BibleCrawler()
        self.crawler.bible_num = 1
        self.crawler.primary_key = 101
        self.crawler.chapter_num = 1

    # --- HTML 문서 가져오기 --- #

    def test_make_payload(self):
        """
        payload 값을 결정하는 함수가 조건에 따라 다르게 작동하는지 테스트
        :return: None
        """
        self.crawler.commit = False
        payload = self.crawler.make_payload()
        self.assertEqual(len(payload), 1)

        self.crawler.commit = True
        payload_item = self.crawler.make_payload()
        self.assertEqual(len(payload_item), 3)

    def test_requests_from_catholic_goodnews(self):
        """
        Request 객체가 정상적으로 생성되어 200 응답코드를 주는지 테스트
        :return: None
        """
        self.crawler.commit = False
        requests = self.crawler.requests_from_catholic_goodnews()
        self.assertEqual(requests.status_code, 200)

        self.crawler.commit = True
        requests_item = self.crawler.requests_from_catholic_goodnews()
        self.assertEqual(requests_item.status_code, 200)

    def test_soup_is_exist(self):
        """
        BeautifulSoup 객체가 정상적으로 생성되는지 테스트
        :return: None
        """
        self.crawler.commit = False
        soup = self.crawler.soup_from_requests()
        self.assertFalse(soup.can_be_empty_element)

        self.crawler.commit = True
        soup_item = self.crawler.soup_from_requests()
        self.assertFalse(soup_item.can_be_empty_element)

    # --- 성경 정보를 결정하기 위한 데이터 크롤링 --- #

    def test_list_contents_from_soup(self):
        """
        soup 객체에서 가져온 contents 객체가 구약성경, 신약성경에 따라 필요없는 요소를 잘 제거하는가
        :return: None
        """
        self.crawler.commit = False

        self.crawler.bible_num = 1
        list_contents_old = self.crawler.list_contents_from_soup()
        self.assertEqual(len(list_contents_old), 46)

        self.crawler.bible_num = 2
        list_contents_new = self.crawler.list_contents_from_soup()
        self.assertEqual(len(list_contents_new), 27)

    def test_book_info_from_list_contents(self):
        """
        contents 객체로부터 book_info 리스트가 잘 생성되는지 테스트
        :return:
        """
        self.crawler.commit = False

        self.crawler.bible_num = 1
        book_info_old = self.crawler.book_info_from_list_contents()
        self.assertEqual(len(book_info_old), 46)

        self.crawler.bible_num = 2
        book_info_new = self.crawler.book_info_from_list_contents()
        self.assertEqual(len(book_info_new), 27)

    def test_pks_from_book_list(self):
        """
        book_info 리스트에서 pk 리스트를 잘 가져오는지 테스트
        :return: None
        """
        self.crawler.commit = False

        self.crawler.bible_num = 1
        pks_old = self.crawler.pks_from_book_info()
        li = [i for i in pks_old]
        self.assertEqual(len(li), 46)

        self.crawler.bible_num = 2
        pks_new = self.crawler.pks_from_book_info()
        li = [i for i in pks_new]
        self.assertEqual(len(li), 27)

    def test_names_from_book_info(self):
        """
        book_info 리스트에서 성경책 이름을 잘 가져오는지 테스트
        :return: None
        """
        self.crawler.commit = False

        self.crawler.bible_num = 1
        names_old = self.crawler.names_from_book_info()
        li = [i for i in names_old]
        self.assertEqual(len(li), 46)

        self.crawler.bible_num = 2
        names_new = self.crawler.names_from_book_info()
        li = [i for i in names_new]
        self.assertEqual(len(li), 27)

    def test_chapters_from_list_contents(self):
        """
        contents 리스트에서 chapter 리스트를 잘 가져오는지 테스트
        :return: None
        """
        self.crawler.commit = False

        self.crawler.bible_num = 1
        chapters_old = self.crawler.chapters_from_list_contents()
        self.assertEqual(len(chapters_old), 46)

        self.crawler.bible_num = 2
        chapters_new = self.crawler.book_info_from_list_contents()
        self.assertEqual(len(chapters_new), 27)

    def test_namedtuple_from_bible_data(self):
        """
        성경 데이터를 수합하는 네임드튜플 만들기 함수가 잘 작동하는지 테스트
        :return: None
        """
        self.crawler.commit = False

        self.crawler.bible_num = 1
        bible_data_old = self.crawler.make_bible_data()
        self.assertEqual(len(bible_data_old), 46)

        self.crawler.bible_num = 2
        bible_data_new = self.crawler.make_bible_data()
        self.assertEqual(len(bible_data_new), 27)

    # --- 성경 정보가 결정된 이후 본문 크롤링 --- #

    def test_read_contents_is_exist(self):
        """
        soup 객체에서 본문과 절 정보가 담긴 <tbody> 요소를 잘 가져오는지 테스트
        :return: None
        """
        self.crawler.commit = True
        read_contents = self.crawler.read_contents_from_soup()
        self.assertFalse(read_contents.can_be_empty_element)

    def test_paragraphs_from_read_contents(self):
        """
        read_contents에서 성경 절 정보를 잘 가져오는지 테스트
        :return: None
        """
        self.crawler.commit = True
        paragraphs = self.crawler.paragraphs_from_read_contents()
        self.assertIsNotNone(paragraphs)

    def test_texts_from_read_contents(self):
        """
        read_contents에서 성경 본문 정보를 잘 가져오는지 테스트
        :return: None
        """
        self.crawler.commit = True
        texts = self.crawler.texts_from_read_contents()
        self.assertIsNotNone(texts)

    def test_namedtuple_from_bible_info(self):
        """
        모든 요소들이 네임드튜플로 생성되는지 테스트
        :return: None
        """
        self.crawler.commit = False
        self.crawler.make_bible_data()

        self.crawler.commit = True
        bible_info = self.crawler.make_bible_info()
        self.assertEqual(len(bible_info), 31)

    def tearDown(self):
        """
        테스트 끝난 뒤 변수들 초기화
        :return:
        """
        self.crawler.bible_num = None
        self.crawler.primary_key = None
        self.crawler.chapter_num = None


class UITest(unittest.TestCase):
    def setUp(self):
        """
        UI 테스트를 위한 전역변수 설정
        1. self.elements: main.py의 Elements 클래스
        :return:
        """
        self.main = Main()

    def test_make_random_number(self):
        """
        랜덤 숫자가 잘 만들어지는지 테스트
        :return:
        """
        self.main.make_random_number()
        self.assertIsNotNone(self.main.bible_num)
        self.assertIsNotNone(self.main.primary_key)
        self.assertIsNotNone(self.main.chapter_num)

    def test_get_message(self):
        """
        랜덤 메시지 생성 함수가 잘 작동하는지 테스트
        :return:
        """
        self.main.make_random_number()
        self.main.commit = True
        message = self.main.get_message()

        self.assertIsNotNone(message)

    def test_get_input_quit_message_from_start_menu(self):
        """
        input 함수에서 'q' 메시지를 넣었을 때 잘 종료되는지 테스트
        :return:
        """
        user_input = [
            'q',
        ]
        expected_stacks = [
            self.main.validate('q'),
        ]
        with patch('builtins.input', side_effect=user_input):
            stacks = self.main.start_menu()
        self.assertEqual(stacks, expected_stacks[0])


if __name__ == '__main__':
    unittest.main()
