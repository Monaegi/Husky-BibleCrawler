import unittest

import crawler


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        """
        크롤러 테스트를 위한 전역변수 설정
        1. base_url: 크롤링을 하기 위한 가톨릭 굿뉴스 성경 사이트
        2. params: 신약성경, 구약성경 및 각 복음서의 고유 pk 값, 페이지
        3. requests: Requests 객체
        4. soup: BeautifulSoup 객체
        :return: None
        """
        self.base_url = crawler.BASE_URL
        self.params = crawler.PAYLOAD
        self.requests = crawler.requests_from_catholic_goodnews(
            url=self.base_url,
            payload=self.params,
        )
        self.soup = crawler.soup_from_requests(self.requests)
        self.generator = crawler.texts_from_soup(self.soup)

    def test_requests_from_catholic_goodnews(self):
        """
        Request 객체가 정상적으로 생성되어 200 응답코드를 주는지 테스트
        :return: None
        """
        requests = self.requests
        self.assertEqual(requests.status_code, 200)

    def test_soup_is_exist(self):
        """
        BeautifulSoup 객체가 정상적으로 생성되는지 테스트
        :return: None
        """
        soup = self.soup
        self.assertFalse(soup.can_be_empty_element)

    def test_select_texts_from_soup(self):
        """
        BS 객체에서 뽑아낸 성경 구절 튜플이 정상적으로 생성되는지 테스트
        :return:
        """
        gen = self.generator
        li = [i for i in gen]
        self.assertIsNotNone(li)

    def test_select_primary_key_of_gospel(self):
        """
        복음서의 pk값과 복음서 이름을 OrderedDict로 크롤링한 것이 정상적으로 생성되는지 테스트
        :return:
        """
        ordered_dict = crawler.primary_key_of_gospel(self.soup)
        self.assertEqual(len(ordered_dict), 4)


    def test_namedtuple_from_list(self):
        """
        list의 요소들에 복음서와 구절 숫자를 입혀 네임드튜플로 생성되는지 테스트
        :return: None
        """
        namedtuple = crawler.make_namedtuple(self.generator)
        self.assertIsNotNone(namedtuple)

if __name__ == '__main__':
    unittest.main()
