import requests, json
from bs4 import BeautifulSoup


def get_link_to_file(s):
    return s.replace('/attach/', 'https://hw.iu9.bmstu.ru/attach/').replace('/static/',
                                                                            'https://hw.iu9.bmstu.ru/static/')


LANG_TO_ID = {
    'C': 1,
    'Scheme': 2,
    'Go': 3,
    'Java': 4,
    'C++': 5,
    'Markdown': 6,
}

STRING_TO_VERDICT = {
    'Тесты пройдены': 'passed',
    'Отклонено преподавателем': 'banned',
    'Зачтено': 'accepted',
    'Тесты не пройдены': 'failed',
    'Ожидает проверки': 'waiting',
}


class ServerConnection:
    password: str

    def __init__(self, login, password):
        self.username = None
        self.login = login
        self.password = password

        self.session = requests.Session()

        r = self.session.post('https://hw.iu9.bmstu.ru/auth',
                              data={
                                  'login': self.login,
                                  'password': self.password,
                              })

    def get_name(self):
        response = self.session.get('https://hw.iu9.bmstu.ru/student?course_id=-200')
        html = response.content

        soup = BeautifulSoup(html, 'html.parser')

        elements = soup.find_all('div', class_='paper content')
        self.username = elements[0].text.strip().replace('Студент: ', '')

    @property
    def is_authorized(self) -> bool:
        r = self.session.get('https://hw.iu9.bmstu.ru/student')
        if r.url == 'https://hw.iu9.bmstu.ru/student':
            self.get_name()

            try:
                with open("info.json", "r") as f:
                    info = f.read()
                    settings = json.loads(info)
            except:
                settings = dict()

            settings['username'] = self.login
            settings['password'] = self.password

            with open("info.json", "w") as my_file:
                my_file.write(json.dumps(settings))

            return True
        return False

    def print_text(self):
        print(self.session.get('https://hw.iu9.bmstu.ru/student').text)

    def get_subjects(self):
        response = self.session.get('https://hw.iu9.bmstu.ru/student?course_id=-200')
        html = response.content

        # создаем объект BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        elements = soup.find_all('div', class_='header_menu-element')

        answer = []

        for element in elements:
            a = {
                'link': element.find('a')['href'].replace('/student?course_id=', ''),
                'text': element.text.strip(),
            }
            answer.append(a)

        return answer

    def get_course_tasks(self, course_id: int) -> str:
        response = self.session.get(f'https://hw.iu9.bmstu.ru/student?course_id={course_id}')
        html = response.content

        # создаем объект BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', {'class': 'tasks_table'})

        answer = {}

        rows = table.find_all('tr')

        lst = []
        num = 1
        for row in rows:
            cols = row.find_all('td')
            to_print = row.text.strip().replace('\n', ' ').replace('\t', '').split()

            if to_print[0] == 'Модуль' or to_print[0] == 'Сумма':
                if lst:
                    answer[f'Модуль {num}'] = lst
                    num += 1
                    lst = []
                continue
            if len(cols[1].attrs['class']) > 1:
                verdict = cols[1].attrs['class'][1].replace('score_', '')
            else:
                verdict = 'nonsolved'
            lst.append(
                {
                    'name': to_print[0],
                    'degree': to_print[1],
                    'max': to_print[2],
                    'verdict': verdict,
                    'link': row.find_all('td')[0].find('a')['href'].replace('/submission?task_id=', ''),
                }
            )

        return answer

    def get_task_by_id(self, task_id):
        response = self.session.get(f'https://hw.iu9.bmstu.ru/submission?task_id={task_id}')
        html = response.content

        # создаем объект BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # получаем условие задачи
        task = soup.find('div', {'class': 'paper content'}).find('div')

        # получаем ЯП, на которых ее можно сдать
        labels = soup.find_all('label')

        languages = []
        for label in labels:
            if label.attrs['for'].startswith('lang'):
                languages.append(label.text)

        submissions = []
        # получаем попытки решения
        tries = soup.find_all('details', {'class': 'test-result_details'})
        for tri in tries:
            summary_text = tri.summary.text.strip().split()
            submissions.append(
                {
                    'date': summary_text[1] + " " + summary_text[2][:-1],
                    'verdict': STRING_TO_VERDICT[' '.join(summary_text[3:])],
                    'id': len(submissions),
                    'lang': tri.find('div').text.split('\n')[1].replace('Язык реализации: ', ''),
                }
            )

        return get_link_to_file(str(task)), languages, submissions

    def sumbit_solution(self, task_id, code, language):
        r = self.session.post(f' https://hw.iu9.bmstu.ru/submission?task_id={task_id}',
                              data={
                                  'lang': LANG_TO_ID[language],
                                  'submission': code,
                              })
        return r.status_code

    def get_task_report(self, task_id, code_id):
        response = self.session.get(f'https://hw.iu9.bmstu.ru/submission?task_id={task_id}')
        html = response.content

        soup = BeautifulSoup(html, 'html.parser')

        task_name = soup.find('h1').text

        details = soup.find_all('details', {'class': 'test-result_details'})[code_id]

        code = details.find('div').find('div', {'class', 'test-result_code-block'})

        verdict = STRING_TO_VERDICT[' '.join(details.summary.text.strip().split()[3:])]

        antiplagiate = 'noinf'
        if verdict == 'passed':
            antiplagiate = details.find('div').find_all('p')[1].text.replace('Антиплагиат: ', '')

        comment = 'noinf'
        if verdict == 'accepted' or verdict == 'banned':
            antiplagiate = details.find('div').find_all('p')[1].text.replace('Антиплагиат: ', '')
            comment = details.find('div').find_all('p')[2].text

        lang = details.find('div').p.text.replace('Язык реализации: ', '')

        report = str(details.find('div').find_all('details', {'class': 'test-result_paragraph'})[1]
                     .find('div')).replace('/attach/', 'https://hw.iu9.bmstu.ru/attach/')
        if '<div class="form_code-submit-wrapper">' in report:
            i = report.index('<div class="form_code-submit-wrapper">')
            s = ''
            while not '</div>' in s:
                s += report[i]
                i += 1

            report = report.replace(s, '')

        return code, task_name, verdict, lang, report, antiplagiate, comment
