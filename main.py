import random

from crawler import BibleCrawler


class Elements:
    """
    UI 환경에 사용하는 텍스트, 실행 바 등등을 정의하는 함수
    :return: None
    """

    def __init__(self):
        self.main_bar = '=' * 52
        self.main_title = '가톨릭 말씀사탕'.center(47, ' ')
        self.crawler = BibleCrawler()

    def call_crawler_soup(self, bible_num, primary_key=None, chapter_num=None, commit=False):
        """
        크롤러 soup 객체를 가져온다
        :param bible_num: 1. 구약성경, 2: 신약성경
        :param primary_key: 성경책의 고유 pk 값
        :param chapter_num: 성경 장
        :param commit: 본문을 가져올 것인가(True), 리스트를 가져올 것인가(False)
        :return: 용도에 맞는 soup 객체
        """
        d = self.crawler.make_payload(bible_num, primary_key, chapter_num, commit=commit)
        r = self.crawler.requests_from_catholic_goodnews(d)
        return self.crawler.soup_from_requests(r)

    def call_bible_data(self, soup, bible_num, primary_key):
        """
        성경책이 지니고 있는 총 챕터 숫자를 가져온다
        :param soup: soup 객체
        :param bible_num: 1. 구약성경, 2: 신약성경
        :param primary_key: 성경책의 고유 pk 값
        :return: 성경책이 지니고 있는 총 챕터 숫자
        """
        li = self.crawler.list_contents_from_soup(soup, bible_num)
        b = self.crawler.book_info_from_list_contents(li)
        k = self.crawler.pks_from_book_info(b)
        n = self.crawler.names_from_book_info(b)
        c = self.crawler.chapters_from_list_contents(li)
        bible_dict = self.crawler.make_bible_data(k, n, c)
        return bible_dict[primary_key]

    def call_bible_info(self, soup, bible_data, rand_num):
        """
        성경 본문을 가져오는 함수
        :param soup: soup 객체
        :param bible_data: 성경 정보가 담긴 네임드튜플
        :param rand_num: 성경 정보가 담긴 랜덤 숫자
        :return:
        """
        re = self.crawler.read_contents_from_soup(soup)
        p = self.crawler.paragraphs_from_read_contents(re)
        t = self.crawler.texts_from_read_contents(re)
        return self.crawler.make_bible_info(bible_data, rand_num, p, t)

    def make_random_number(self):
        """
        성경 숫자를 랜덤으로 만들어낼 함수
        :return:
        """
        # 구약성경: 1, 신약성경: 2
        bible_num = random.randint(1, 2)
        # 성경책 pk: 구약성경일 경우 101~146 사이, 신약성경일 경우 147~173 사이
        primary_key = random.randint(101, 146) if bible_num is 1 else random.randint(147, 173)
        # 장 넘버: 성경책 pk를 통해 알게 된 성경책이 총 몇 개의 장을 가지고 있는지 알아내고,
        # 그 숫자를 범위로 하는 랜덤 숫자를 가져온다
        soup = self.call_crawler_soup(bible_num)
        chapters_count = self.call_bible_data(soup, bible_num, primary_key).chapters_count
        chapter_num = random.randint(1, chapters_count)

        return bible_num, primary_key, chapter_num

    def start_menu(self):
        """
        시작 메뉴
        :return:
        """
        print('\n말씀사탕에 오신 것을 환영합니다.')
        print('사탕을 받으려면 "go"를 입력해주세요!\n나가시려면 "q"를 입력해주세요.')
        user_input = input('[go/q]: ')

        return self.validate(user_input)

    def validate(self, input_data):
        """
        사용자에게 입력받은 값이 유효한지 검증함
        :param input_data: 사용자에게 입력받은 값
        :return:
        """
        if input_data == 'go':
            # 'go'를 입력하면 크롤링을 요청해 말씀을 꺼내온다
            return self.get_message()
        elif input_data == 'q':
            # 'q'를 입력하면 프로그램 종료
            print('\n다음에 다시 만나요!\n')
            return None
        else:
            # 유효하지 않은 값이 들어오면 알려주고 메뉴로 돌려보낸다
            print('\n올바른 값을 입력하세요!\n')
            return self.start_menu()

    def get_message(self):
        """
        크롤러에서 랜덤으로 말씀을 가져온다
        :return: 말씀 객체
        """
        # 랜덤 숫자를 가져온다
        rand_num = self.make_random_number()
        # 랜덤 숫자를 언패킹
        bn, pk, cn = rand_num

        # 랜덤 숫자를 기반으로 성경 구절을 가져온다
        soup_list = self.call_crawler_soup(bn)
        soup_item = self.call_crawler_soup(bn, pk, cn, commit=True)
        bible_data = self.call_bible_data(soup_list, bn, pk)
        bible_info = self.call_bible_info(soup_item, bible_data, rand_num)
        result = random.choice(bible_info)

        print(f'\n\n{result.texts} ({result.books_name} {result.chapter_num}-{result.paragraph_num})\n')

        return self.start_menu()


def main():
    """
    크롤러 실행 UI 함수
    :return: None
    """
    e = Elements()
    print(e.main_bar)
    print(e.main_title)
    print(e.main_bar)
    e.start_menu()


if __name__ == '__main__':
    main()
