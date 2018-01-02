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

    def test_requests_from_catholic_goodnews(self):
        r = self.requests
        self.assertEqual(r.status_code, 200)

    def test_soup_is_exist(self):
        soup = crawler.soup_from_requests(self.requests)
        self.assertFalse(soup.can_be_empty_element)


if __name__ == '__main__':
    unittest.main()
