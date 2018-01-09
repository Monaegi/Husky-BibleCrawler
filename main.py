import random

from crawler import BibleCrawler


class Main(BibleCrawler):
    """
    실행을 위한 메인 클래스
    """

    # --- 크롤러 실행 함수 --- #

    def make_random_number(self):
        """
        성경 숫자를 랜덤으로 만들어낼 함수
        :return: 랜덤 chapter_num
        """
        # 구약성경: 1, 신약성경: 2
        self.bible_num = random.randint(1, 2)
        # 성경책 pk: 구약성경일 경우 101~146 사이, 신약성경일 경우 147~173 사이
        self.primary_key = random.randint(101, 146) if self.bible_num is 1 else random.randint(147, 173)
        # payload를 False로 세팅한다
        self.commit = False
        # 장 넘버: 성경책 pk를 통해 알게 된 성경책이 총 몇 개의 장을 가지고 있는지 알아내고,
        # 그 숫자를 범위로 하는 랜덤 숫자를 가져온다
        chapters_count = self.make_bible_data()[self.primary_key].chapters_count
        self.chapter_num = random.randint(1, int(chapters_count))

        return self.chapter_num

    def get_message(self):
        """
        크롤러에서 랜덤으로 말씀을 가져온다
        :return: 말씀 객체
        """
        # 랜덤 숫자를 기반으로 성경 구절을 가져온다
        bible_info = self.make_bible_info()
        result = random.choice(bible_info)

        print(f'\n\n{result.texts} ({result.books_name} {result.chapter_num}-{result.paragraph_num})\n')
        return result

    # --- 프로그램 실행 함수 --- #

    def start_menu(self):
        """
        시작 메뉴
        :return: 사용자가 입력한 값을 인자로 하는 validate 함수
        """
        main_bar = '=' * 52

        print(main_bar)
        print('가톨릭 말씀사탕'.center(47, ' '))
        print(main_bar)
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
        while input_data != 'q':
            if input_data == 'go':
                # 랜덤 숫자를 구한다
                self.make_random_number()
                # payload의 옵션을 바꾸기 위해 commit=True로 맞춘다
                self.commit = True
                # 'go'를 입력하면 크롤링을 요청해 말씀을 꺼내온다
                self.get_message()
            else:
                # 유효하지 않은 값이 들어오면 알려주고 메뉴로 돌려보낸다
                print('\n올바른 값을 입력하세요!\n')
            return self.start_menu()

        # 'q'를 입력하면 프로그램 종료
        print('\n다음에 다시 만나요!\n')
        return None


if __name__ == '__main__':
    Main().start_menu()
