import sqlite3


class DB:
    """
    database를 다루는 클래스
    """

    def __init__(self):
        self.__db_name = 'bible.db'
        self.__conn = None
        self.__create_table_commands = {
            'bible_data': """ CREATE TABLE IF NOT EXISTS bible_data (
                              id INTEGER PRIMARY KEY,
                              bible_pk INTEGER NOT NULL,
                              name TEXT NOT NULL,
                              chapter_count INTEGER NOT NULL
                              ); """,
            'bible_info': """ CREATE TABLE IF NOT EXISTS bible_info (
                              id INTEGER PRIMARY KEY,
                              name TEXT NOT NULL,
                              chapter_num INTEGER NOT NULL,
                              paragraph_num INTEGER NOT NULL,
                              texts TEXT NOT NULL,
                              FOREIGN KEY (name) REFERENCES bible_data (name)
                              ); """
        }

    # --- 네임 맹글링 --- #

    @property
    def db_name(self):
        return self.__db_name

    @db_name.setter
    def db_name(self, input_db_name):
        self.__db_name = input_db_name

    @property
    def conn(self):
        return self.__conn

    @conn.setter
    def conn(self, input_connection):
        self.__conn = input_connection

    @property
    def create_table_commands(self):
        return self.__create_table_commands

    # --- 인스턴스 메서드 ---#

    def create_db_connection(self):
        """
        database 생성 및 연결 함수
        :return: sqlite3.Connection 객체
        """
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def create_data_table(self):
        """
        bible_data 테이블을 생성하는 함수
        :return: None
        """
        # sqlite3 connection 객체 생성
        conn = self.conn if self.conn else self.create_db_connection()
        # cursor 객체 가져오기
        cursor = conn.cursor()
        print('DB table을 생성합니다...')
        cursor.execute(self.create_table_commands['bible_data'])
        cursor.execute(self.create_table_commands['bible_info'])
        print('DB table 생성 완료')
        return None

    def insert_bible_data_into_db(self, bible_data):
        """
        bible_data를 db 안에 넣는 함수
        :param bible_data: 크롤러가 생성한 bible_data
        :return: None
        """
        # sql 명령문: bible_data 테이블에 해당하는 값을 넣어라
        sql_command = """ INSERT INTO bible_data(bible_pk, name, chapter_count) VALUES(?,?,?) """
        # db에 넣을 값: bible_data에서 db에 넣을 수 있는 튜플 형태로 재변환
        data_comp = ((book, bible_data[book].books_name, bible_data[book].chapters_count) for book in bible_data)

        # 커서를 꺼내 data_comp를 순회하며 db에 정보를 넣는다
        conn = self.conn if self.conn else self.create_db_connection()
        cursor = conn.cursor()
        try:
            print('성경 데이터를 DB에 추가합니다...')
            for data in data_comp:
                cursor.execute(sql_command, data)
            print('성경 데이터 추가 완료')
            return None
        # 예외처리: data_table이 없을 경우
        except sqlite3.Error as e:
            print(e)
            return e

    def insert_bible_info_into_db(self, bible_info):
        """
        bible_info를 db 안에 넣는 함수
        :param bible_info:
        :return: None
        """
        # sql 명령문: bible_info 테이블에 해당하는 값을 넣어라
        sql_command = """ INSERT INTO bible_info(name, chapter_num, paragraph_num, texts) VALUES(?,?,?,?) """
        # db에 넣을 값: bible_info에서 db에 넣을 수 있는 튜플 형태로 재변환
        info_comp = ((info.books_name, info.chapter_num, info.paragraph_num, info.texts) for info in bible_info)

        # 커서를 꺼내 info_comp를 순회하며 db에 정보를 넣는다
        conn = self.conn if self.conn else self.create_db_connection()
        cursor = conn.cursor()
        try:
            print('성경 정보를 DB에 추가합니다...')
            for info in info_comp:
                cursor.execute(sql_command, info)
            print('성경 정보 추가 완료')
            return None
        # 예외처리: data_table이 없을 경우
        except sqlite3.Error as e:
            print(e)
            return e

    def search_bible_data_from_db(self, primary_key):
        """
        db에서 bible_data를 검색하는 함수
        :return: data가 있으면: primary Key에 해당하는 성경책의 chapter_count, 없으면: None
        """
        # sql 명령문: bible_data 테이블에서 입력한 primary_key 값에 해당하는 chapter_count를 출력하라
        sql_command = """ SELECT chapter_count FROM bible_data WHERE bible_pk=%d """ % primary_key

        # 커서를 꺼내 db를 검색한다
        conn = self.conn if self.conn else self.create_db_connection()
        cursor = conn.cursor()
        try:
            print('성경 데이터를 검색합니다...')
            data = cursor.execute(sql_command)
            result_comp = [count for count in data]

            # 값이 검색되면 성공 메시지를 출력하고 chapter_count를 리턴한다
            if len(result_comp) is 1:
                print('성경 데이터 검색 완료')
                return result_comp[0][0]
            else:
                print('DB에 성경 데이터가 없습니다. 웹 검색을 시작합니다...')
                return None

        # 예외처리: data_table이 없을 경우
        except sqlite3.Error as e:
            print(e)
            return e


if __name__ == '__main__':
    pass
