from requests_html import HTMLSession
from datetime import datetime, timedelta
import hashlib
import json
from selenium import webdriver
from time import sleep


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
        return int(len(data['callDetails'])), int(i)

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
        return int(len(data['callDetails']))

    def get_call(self, login, pas, start_time=None, stop_time=None):
        '''
        Очень странно, но в своём API бинотел не реализовал возможность получения статистики Get Call звонков.
        Не проблема. Получим её через админку ))
        :param login: Логин в Бинотеле
        :param pas: Пароль в Бинотеле
        :param start_time: Начало периода. Формат d.m.Y Если не указать, данные будут за вчера
        :param stop_time:  Конец периода. Формат d.m.Y Если не указать, данные будут за вчера
        '''
        start_time = start_time or self.yesterday
        stop_time = stop_time or self.yesterday

        start = start_time.split('.')
        stop = stop_time.split('.')

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('window-size=1920x935')
        driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)

        driver.get(f'https://my.binotel.ua/?module=gcStatistics&startDay={start[0]}&startMonth={start[1]}&\
                   startYear={start[2]}&stopDay={stop[0]}&stopMonth={stop[1]}&stopYear={stop[2]}')
        sleep(1)
        logining = driver.find_element_by_name('logining[email]')
        password = driver.find_element_by_name('logining[password]')
        button = driver.find_element_by_name('logining[submit]')

        logining.send_keys(login)
        password.send_keys(pas)
        button.click()
        sleep(1)

        stat_link = driver.find_element_by_class_name('short-statistics-button')
        stat_link.click()
        sleep(1)

        all_call = driver.find_element_by_xpath("//div[contains(@class, 'shortStatisticsData')]/p[1]/b")
        new_call = driver.find_element_by_xpath("//div[contains(@class, 'shortStatisticsData')]/p[2]/b")

        return int(all_call.text), int(new_call.text)
