import unittest

import crawler


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        """
        크롤러 테스트를 위한 전역변수 설정
        1. base_url: 크롤링을 하기 위한 가톨릭 굿뉴스 성경 사이트
        2. params: 신약성경, 구약성경 및 각 성경책의 고유 pk 값, 페이지
        3. requests: Requests 객체
        4. soup: BeautifulSoup 객체
        5. dict: 성경책 이름과 고유 pk로 이루어진 dict
        6. generator: 성경 절과 본문 튜플이 담긴 generator
        7. namedtuple: 모든 요소를 통합해서 만든 namedtuple
        :return: None
        """
        self.base_url = crawler.BASE_URL
        self.params = crawler.PAYLOAD
        self.requests = crawler.requests_from_catholic_goodnews(
            url=self.base_url,
            payload=self.params,
        )
        self.soup = crawler.soup_from_requests(self.requests)
        self.dict = crawler.primary_key_of_gospel(self.soup)
        self.generator = crawler.texts_from_soup(self.soup)
        self.namedtuple = crawler.make_namedtuple(self.dict, self.generator)

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


if __name__ == '__main__':
    unittest.main()
