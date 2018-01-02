import unittest

import crawler


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        self.base_url = crawler.BASE_URL
        self.params = crawler.PAYLOAD
        self.requests = crawler.requests_from_catholic_goodnews(
            url=self.base_url,
            payload=self.params,
        )
        self.soup = crawler.soup_from_requests(self.requests)

    def test_requests_from_catholic_goodnews(self):
        requests = self.requests
        self.assertEqual(requests.status_code, 200)

    def test_soup_is_exist(self):
        soup = self.soup
        self.assertFalse(soup.can_be_empty_element)

    def test_select_texts_from_soup(self):
        li = crawler.texts_from_soup(self.soup)
        self.assertEqual(type(li), type(list()))


if __name__ == '__main__':
    unittest.main()
