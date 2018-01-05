import random


class Elements:
    """
    UI 환경에 사용하는 텍스트, 실행 바 등등을 정의하는 함수
    :return: None
    """

    def __init__(self):
        self.main_bar = '=' * 52
        self.main_title = '가톨릭 말씀사탕'.center(47, ' ')

    def start_menu(self):
        """
        시작 메뉴
        :return:
        """
        welcome = '\n말씀사탕에 오신 것을 환영합니다.'
        choice_msg = '사탕을 받으려면 "go"를 입력해주세요!\n나가시려면 "q"를 입력해주세요.'
        print(welcome)
        print(choice_msg)
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
            print('\n다음에 다시 만나요!')
            return None
        else:
            # 유효하지 않은 값이 들어오면 알려주고 메뉴로 돌려보낸다
            print('\n올바른 값을 입력하세요!')
            return self.start_menu()

    def get_message(self):
        """
        크롤러에서 랜덤으로 말씀을 가져온다
        :return: 말씀 객체
        """

        def make_random_number():
            """
            성경 숫자를 랜덤으로 만들어낼 함수
            :return:
            """
            bible_num = random.randint(1, 2)

            book_num = random.randint(101, 146) if bible_num is 1 else random.randint(147, 173)

            return bible_num, book_num

        print(make_random_number())


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
