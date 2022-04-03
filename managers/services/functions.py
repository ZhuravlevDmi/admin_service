import datetime
import re

import requests

from loguru import logger
from passwords_dir.passwords import jira_db_corp_replica
from utils_dir.Classes.Postgres import Postgres
from utils_dir.config import url_send_sms
from utils_dir.sql_queries import check_user_jira, additionalPhoneNumber, phone_number_client, time_issue_create

jira_corp_db = Postgres(jira_db_corp_replica['database'],
                        jira_db_corp_replica['user'],
                        jira_db_corp_replica['password'],
                        jira_db_corp_replica['host'])


def check_jira_user(login: str, db_jira: Postgres) -> bool:
    # функция принимает логин ad, если по такому логину не нашлась учетка в jira, возвращаем False
    try:
        if db_jira.connect_to_db():
            info = db_jira.get_data(check_user_jira.format(login))
            db_jira.close_connection()
            if info:
                return True
        return False
    except Exception as e:
        db_jira.close_connection()
        logger.critical(f'{e}')


def get_additionalPhoneNumber(login: str, db_jira: Postgres) -> str:
    # функция принимает логин ad, если по такому логину не нашлась учетка в jira, возвращаем False
    try:
        if db_jira.connect_to_db():
            info = db_jira.get_data(additionalPhoneNumber.format(login))
            db_jira.close_connection()
            if info:
                num = info[0][0]
                return num
        return ''
    except Exception as e:
        db_jira.close_connection()
        logger.critical(f'{e}')
        return ''


def get_phone_number_client(issue_num: str, db_jira: Postgres) -> str:
    # функция принимает номер задачи, достает номер клиента
    try:
        if db_jira.connect_to_db():
            info = db_jira.get_data(phone_number_client.format(issue_num))
            db_jira.close_connection()
            if info:
                num = info[0][0]
                return num
        return ''
    except Exception as e:
        db_jira.close_connection()
        logger.critical(f'{e}')
        return ''


def get_time_create_issue(issue_num: str, db_jira: Postgres) -> str:
    # функция принимает номер задачи, и возвращает время создание задачи
    try:
        if db_jira.connect_to_db():
            info = db_jira.get_data(time_issue_create.format(issue_num))
            db_jira.close_connection()
            if info:
                num = info[0][0]
                return num
        return ''
    except Exception as e:
        db_jira.close_connection()
        logger.critical(f'{e}')
        return ''


def check_day_week() -> str | None:
    """
    Функция определяет день недели
    :return:
    """
    today = datetime.datetime.now()
    week_day = today.isoweekday()

    match week_day:
        case 1:
            week_day_str = 'monday'
        case 2:
            week_day_str = 'tuesday'
        case 3:
            week_day_str = 'wednesday'
        case 4:
            week_day_str = 'thursday'
        case 5:
            week_day_str = 'friday'
        case 6:
            week_day_str = 'saturday'
        case 7:
            week_day_str = 'sunday'
        case _:
            return None
    return week_day_str


def send_sms_code(phone_number: str, additionalPhoneNumber: str, issue_num: str, feedback_period: str,
                  full_name_manager: str, token: str) -> int:
    """Отправка смс на номер {number}, авторизация по токену ЭК5 + number должен начинаться с +7"""
    url = url_send_sms
    headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json; charset=utf-8'
    }
    data = {
        "recipient": phone_number,
        "receiverType": None,
        "templateGroupId": 137,
        "templateParams": [
            {
                "key": "additionalPhoneNumber",
                "value": additionalPhoneNumber
            },
            {
                "key": "task.number",
                "value": issue_num
            },
            {
                "key": "feedback.period",
                "value": feedback_period
            },
            {
                "key": "manager.name",
                "value": full_name_manager
            }],
        "contragentId": None,
        "sellerId": None,
        "countryCode": 1,
        "templateLang": None,
        "orderNumbers": None,
        "orderOnlineShopNumbers": None
    }
    r = requests.post(url=url, json=data, headers=headers)
    logger.info(r.text)
    if r.status_code > 299:
        logger.error(f'Func send_sms_code_v2: \n{r.status_code=} \n{r.text} \nnum')
    else:
        logger.info(f'Func send_sms_code_v2: \n{r.status_code=}, success')
    return r.status_code


def validation_phone_number(phone_number: str) -> str | bool:
    phone_number = "".join(c for c in phone_number if c.isdecimal())

    try:
        if phone_number[0] == "+":
            int(phone_number[1:])
        int(phone_number)
    except ValueError:
        logger.error('Номер телефона состоит не из цифр')
        return False

    if phone_number[0:2] == '79' and len(phone_number) == 11:
        return '+' + phone_number
    elif phone_number[0:1] == '9' and len(phone_number) == 10:
        return '+7' + phone_number
    elif phone_number[0:2] == '89' and len(phone_number) == 11:
        return '+7' + phone_number[1:]
    else:
        return False


def check_times(start: int, finish: int) -> bool:
    """
    Функция проверяет время от старта до финиша, если попадаем в этот интервал, возвращаем True
    :param start: час с которого начинается отсчет
    :param finish: час которым заканчивается отсчет
    :return: True or Flase
    """
    start = datetime.time(hour=start)
    finish = datetime.time(hour=finish)
    now = datetime.datetime.now().time()

    if start < now < finish:
        logger.info('Рабочее время для отправки СМС')
        return True
    else:
        logger.info('Не рабочее время для отправки СМС')
        return False
