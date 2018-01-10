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
        try:
            cursor.execute(self.create_table_commands['bible_data'])
            cursor.execute(self.create_table_commands['bible_info'])
            print('DB table 생성 완료')
        except sqlite3.Error as e:
            print(e)

    def insert_bible_data_into_db(self, bible_data):
        """
        bible_data를 db 안에 넣는 함수
        :param bible_data: 크롤러가 생성한 bible_data
        :return:
        """
        sql_command = """ INSERT INTO bible_data(bible_pk, name, chapter_count) VALUES(?,?,?) """

        data_comp = ((book, bible_data[book].books_name, bible_data[book].chapters_count) for book in bible_data)

        conn = self.conn if self.conn else self.create_db_connection()
        cursor = conn.cursor()
        try:
            for data in data_comp:
                cursor.execute(sql_command, data)
            print('bible_data 추가 완료')
        except sqlite3.Error as e:
            print(e)


if __name__ == '__main__':
    d = DB()
