from bs4 import BeautifulSoup
import requests

BASE_URL = 'http://maria.catholic.or.kr/bible/read/bible_read.asp'
PAYLOAD = {
    'm': 2,  # 1: 구약성경, 2: 신약성경 ...
    'n': 147,  # 전체 성경 각 권의 pk 값
    'p': 1,  # 페이지
}


def requests_from_catholic_goodnews(url, payload):
    """
    가톨릭 굿뉴스 사이트에서 리퀘스트 객체를 받아온다
    :param url: request를 받을 url
    :param payload: parameter 값
    :return: requests 객체
    """
    return requests.get(url, params=payload)


if __name__ == '__main__':
    r = requests_from_catholic_goodnews(BASE_URL, PAYLOAD)
    print(r)
