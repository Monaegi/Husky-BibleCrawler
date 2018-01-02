import unittest

import crawler


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        self.base_url = crawler.BASE_URL
        self.params = crawler.PAYLOAD

    def test_requests_from_catholic_goodnews(self):
        r = crawler.requests_from_catholic_goodnews(
            url=self.base_url,
            payload=self.params,
        )
        self.assertEqual(r.status_code, 200)

    def test_soup(self):
        soup = crawler.soup_from_requests()
        self.assertEqual(soup.tag == 1)


if __name__ == '__main__':
    unittest.main()
