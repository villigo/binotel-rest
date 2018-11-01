from requests_html import HTMLSession
from datetime import datetime, timedelta
import hashlib
import json


class CallStats:

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        date = datetime.today() - timedelta(days=1)     # Получаем вчерашнюю дату
        self.yesterday = date.strftime('%d.%m.%Y')

    def incoming_calls(self, start_time=None, stop_time=None):
        start_time = start_time or self.yesterday
        stop_time = stop_time or self.yesterday

        session = HTMLSession()
        api_url = 'https://api.binotel.com/api/2.0/stats/incoming-calls-for-period.json'

        start_time = int(datetime.strptime(f'{start_time} 00:00:00', '%d.%m.%Y %H:%M:%S').timestamp())
        stop_time = int(datetime.strptime(f'{stop_time} 23:59:59', '%d.%m.%Y %H:%M:%S').timestamp())

        params = dict()
        params['startTime'] = start_time
        params['stopTime'] = stop_time
        sort_params = self.secret + json.dumps(params, sort_keys=True).replace(' ', '')
        params['signature'] = hashlib.md5(sort_params.encode('utf-8')).hexdigest()
        params['key'] = self.key
        json_params = json.dumps(params)

        response = session.post(api_url, data=json_params)
        data = response.json()
        i = 0
        for item in data['callDetails']:
            if data['callDetails'][item]['isNewCall'] == '1':
                i += 1
        return len(data['callDetails']), i

    def outgoing_calls(self, start_time=None, stop_time=None):
        start_time = start_time or self.yesterday
        stop_time = stop_time or self.yesterday

        session = HTMLSession()
        api_url = 'https://api.binotel.com/api/2.0/stats/outgoing-calls-for-period.json'

        start_time = int(datetime.strptime(f'{start_time} 00:00:00', '%d.%m.%Y %H:%M:%S').timestamp())
        stop_time = int(datetime.strptime(f'{stop_time} 23:59:59', '%d.%m.%Y %H:%M:%S').timestamp())

        params = dict()
        params['startTime'] = start_time
        params['stopTime'] = stop_time
        sort_params = self.secret + json.dumps(params, sort_keys=True).replace(' ', '')
        params['signature'] = hashlib.md5(sort_params.encode('utf-8')).hexdigest()
        params['key'] = self.key
        json_params = json.dumps(params)

        response = session.post(api_url, data=json_params)
        data = response.json()
        return len(data['callDetails'])
