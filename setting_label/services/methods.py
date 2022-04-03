import os
from time import sleep

from passwords_dir.passwords import jira_rest_api
from utils_dir.Classes.EK5 import EK5
from utils_dir.Classes.Jira import Jira
from utils_dir.Classes.search import Search
from loguru import logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "call_centre_admin_v2.settings")

import django

django.setup()

from setting_label.models import Contract_key_customers


def get_label_key_customers(contract: str) -> str | None:
    """
    функция ищет метку для переданного в функцию договора
    :param contract: номер договора
    :return:
    """

    if contract:
        label = Contract_key_customers.objects.filter(contracts__icontains=contract).first()
        if label:
            return label.label
    return None


def create_list_label(list_label: list, *labels) -> list:
    for label in labels:
        if label:
            list_label.append(label)
    return list_label


def order_analytics(ticket: str, order_num: str, ek5: EK5, jira: Jira) -> dict:
    """
    Заменяет работу "аналитика" по накладной, в функции определяется поиск ли это, дорогостой, ключевой ли клиент,
    по результату проставляются метки в задачу
    :param ticket: номер задачи
    :param order_num: номер накладной
    :param ek5: подключение к эк5
    :param jira: подключение к jira
    :return: результат
    """
    try:
        search = Search(order_number=order_num, ek5=ek5)
    except Exception as e:
        logger.critical(f'{e}')
        logger.critical(f'{ticket=}')
        logger.critical('chhhhhhhhhh')
        ek5.get_user_token()
        try:
            sleep(5)
            search = Search(order_number=order_num, ek5=ek5)
            logger.info('Получилось')
        except Exception as e:
            logger.error(f'Повторная ошибка {e}')
            label_for_group = 'Трейсинг'
            list_label = jira.get_ticket_label(ticket)
            final_list_label = create_list_label(list_label, label_for_group)
            jira.assign_label(final_list_label, ticket)
            return {'result':
                {
                    'ticket': ticket,
                    'label_for_group': label_for_group,
                    'label_key_customers': None,
                    'label_price_order': None
                }
            }

    contract_number = search.contract_number

    # определяем какие метки ставить в задачу
    label_for_group = search.status
    label_price_order = search.declared_value_status
    label_key_customers = get_label_key_customers(contract_number)

    # проставляем в задачу локацию и последний статус
    location = search.order.location22
    status = search.order.last_state7
    jira.add_custom_field(ticket, status, location)

    # проставляем метки в задачу
    sleep(3)
    # достаем метки, которые уже есть в задаче
    list_label = jira.get_ticket_label(ticket)

    # формируем list из меток которые уже были в задаче + наши метки
    final_list_label = create_list_label(list_label, label_for_group, label_price_order, label_key_customers)
    jira.assign_label(final_list_label, ticket)

    logger.info(f'{ticket=} \n'
                f'{label_for_group=} \n'
                f'{label_key_customers=} \n'
                f'{label_price_order=}')

    return {'result':
        {
            'ticket': ticket,
            'label_for_group': label_for_group,
            'label_key_customers': label_key_customers,
            'label_price_order': label_price_order
        }
    }

