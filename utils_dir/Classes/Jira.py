# encoding: utf-8
from requests.auth import HTTPBasicAuth
import json
import requests
from loguru import logger


class Jira:
    def __init__(self, login, password, url_api):
        self.login = login
        self.password = password
        self.api_url = url_api

    def get_info_tickets_to_assign(self, jql: str, limit: int = 100) -> dict:
        jql.replace('"', "'")
        url = self.api_url + 'search'
        auth = HTTPBasicAuth(self.login, self.password)
        data = {"jql": jql, "maxResults": limit, "fields": ["key"]}
        response = requests.post(url=url, auth=auth, json=data)
        r = json.loads(response.text)
        logger.info(f'get_info_tickets_to_assign - {response}')

        if response.status_code > 299:
            logger.critical(f'{r}')
        return r

    def add_transition(self, issue):
        logger.info(f'Переводим задачу в работу {issue}')
        data = {"transition": {"id": "11"}}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f'https://corp.cdek.ru/rest/api/2/issue/{issue}/transitions', json.dumps(data),
                                 headers=headers, auth=(self.login, self.password))
        logger.info(f'add_transition - {response}')
        # r = json.loads(response.text)

        if response.status_code > 299:
            logger.critical(f'{response}')
        return response

    def assign_issue_api(self, issue: str, user_name: str) -> int:
        logger.info(f'Назначаем задачу {issue} на {user_name}')
        url = self.api_url + f"issue/{issue}"

        auth = HTTPBasicAuth(self.login, self.password)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = json.dumps({
            "fields": {
                "assignee": {"name": user_name}
            }
        })

        response = requests.put(url, data=payload, headers=headers, auth=auth)
        logger.info(f'assign_issue_api {issue} - {response}')
        if response.status_code > 299:
            logger.critical(f'{response.text}')
        return response.status_code

    def assign_label(self, topics, ticket):

        headers = {'Content-Type': 'application/json'}
        data = {"fields": {
            "labels": topics
        }}
        r = requests.put(f'https://corp.cdek.ru/rest/api/2/issue/{ticket}', headers=headers,
                         auth=(self.login, self.password), json=data)
        logger.info(f'Status of assignment of label {r}')
        if r.status_code > 299:
            logger.error('Ошибка назначения метки')
            logger.error(r.text)

    def get_ticket_label(self, ticket):
        url = f"https://corp.cdek.ru/rest/api/2/issue/{ticket}"

        auth = HTTPBasicAuth(self.login, self.password)

        response = requests.request(
            "GET",
            url,
            auth=auth
        )
        logger.info(f'{response.status_code}')
        if response.status_code > 299:
            logger.error(response.text)

        ans = json.loads(response.text)

        return ans['fields']["labels"]

    def append_label(self, ticket, label):
        current_labels = self.get_ticket_label(ticket)

        print(f'current_labels: {current_labels}')

        if label not in current_labels:
            current_labels.append(label)

            self.assign_label(current_labels, ticket)

            return True
        else:
            return False

    def add_custom_field(self, ticket, str1, str2):

        headers = {'Content-Type': 'application/json'}
        data = {"fields": {
            "customfield_16600": str1,
            'customfield_16601': str2
        }}
        r = requests.put(f'https://corp.cdek.ru/rest/api/2/issue/{ticket}', headers=headers,
                         auth=(self.login, self.password), json=data)
        logger.info(r)
