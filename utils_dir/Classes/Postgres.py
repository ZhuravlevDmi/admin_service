# encoding: utf-8
import psycopg2
from loguru import logger

"""Объекты данного класса являются, подключением к БД, при создании объекта класса Postgres
в параметры передаются database, user, password, host, port"""


class Postgres:
    """Postgres"""

    def __init__(self, database, user, password, host, port=5432):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect_to_db(self) -> bool:
        """
        через данный метод подключаемся к БД
        :return: Null
        """
        try:
            self.con = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host,
                                        port=self.port)
            self.cursor = self.con.cursor()
            logger.info("Connect to db: " + 'host: ' + self.host + ', database: ' + self.database)

            return True
        except psycopg2.OperationalError:
            logger.critical(f'Ошибка в подключении, host: {self.host}')
            return False


    def get_data(self, sql):
        """
        в параметры передаем SQL запрос(SELECT)
        :param sql: SQL запрос(SELECT)
        :return: метод возвращает ответ от SQL запроса, переданного в параметрах методах
        """
        self.cursor.execute(sql)

        data = self.cursor.fetchall()

        return data

    def insert_data(self, sql):
        """
        через данный метод записываем инфу в БД
        :param sql: SQL запрос(INSERT)
        :return:
        """
        self.cursor.execute(sql)
        self.con.commit()
        logger.info(f'Запись в БД {sql}')

    def close_connection(self):
        """
        Отключение от БД
        :return:
        """
        self.con.close()
        self.cursor.close()
        logger.info("Close connection: " + 'host: ' + self.host + ', database: ' + self.database)


    def get_id(self, name_column_id, name_table):
        id = self.get_data(f'''select MAX({name_column_id})
    from {name_table}''')[0][0]

        logger.info(f'Достали id, таблица {name_table}')

        return id

