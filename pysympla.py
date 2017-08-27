import re

import requests
from bs4 import BeautifulSoup


class Sympla:
    BASE_URL = 'https://www.sympla.com.br'
    URLS = {
        'LOGIN': BASE_URL + '/access/login',
        'PARTICIPANTS': BASE_URL + '/participantes-evento',
        'EVENTS': BASE_URL + '/meus-eventos',
    }

    def __init__(self, username, password):
        self._authenticate(username, password)

    def _authenticate(self, username, password):
        data = {
            'username': username,
            'password': password,
            'rememberMe': True,
        }
        headers = {'X-Requested-With': 'XMLHttpRequest',}
        response = requests.post(self.URLS['LOGIN'], data=data, headers=headers)
        if response.status_code == 200:
            self.cookies = response.cookies
        else:
            raise Exception('Authentication failed. Check your credentials.')

    def get_event(self, id):
        try:
            return Event(self._get_event_html(id))
        except:
            raise Exception('Get event failed. Check event id.')

    def _get_event_html(self, id):
        params = { 'id': id }
        response = requests.get(self.URLS['PARTICIPANTS'], params=params,
                                cookies=self.cookies)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception('Get event failed. Check event id.')

    def get_events(self):
        response = requests.get(self.URLS['EVENTS'], cookies=self.cookies)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html5lib')
            html_id = 'event-grid'
            regex_href = re.compile('/sobre-o-evento')
            events = soup.find(id=html_id).find_all('a', href=regex_href)
            for event in events:
                title = event.get_text()
                id = self._get_id_from_a(event)
                html = self._get_event_html(id)

                yield Event(html, title)
        else:
            raise Exception('Get events failed.')

    def _get_id_from_a(self, a):
        href = a.get_attribute_list('href')[0]
        _, id = href.split('=')
        return id

class Event:
    def __init__(self, html, title=''):
        self._soup = BeautifulSoup(html, 'html5lib')
        self._confirmed_participants = 0
        self._pending_participants = 0
        self._title = title

    @property
    def confirmed_participants(self):
        if not self._confirmed_participants:
            id = 'spanTotalParticipants'
            self._confirmed_participants = self._soup.find(id=id).get_text()
        return self._confirmed_participants

    @property
    def pending_participants(self):
        if not self._pending_participants:
            id = 'spanTotalPendingParticipants'
            self._pending_participants = self._soup.find(id=id).get_text()
        return self._pending_participants

    @property
    def title(self):
        if not self._title:
            id = 'event-title'
            self._title = self._soup.find(id=id).get_text()
        return self._title
