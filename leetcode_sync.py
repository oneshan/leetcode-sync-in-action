import datetime
import os
import random
import time
from typing import Iterator, Dict, Any

from jinja2 import Environment, BaseLoader
import requests

import constants


class LeetcodeSync:
    """ A class to download questions and submissions from LeetCode. """

    def __init__(
            self,
            csrf_token: str,
            leetcode_session: str,
        ) -> None:

        self.last_timestamp = LeetcodeSync._get_last_timestamp()
        self.parser = LeetcodeParser(csrf_token, leetcode_session, self.last_timestamp)

        env = Environment(loader=BaseLoader())
        self.path_template = env.from_string(constants.PATH)
        self.readme_content_template = env.from_string(constants.README_CONTENT)
        self.solution_content_template = env.from_string(constants.SOLUTION_CONTENT)
        self.solution_filename_template = env.from_string(constants.SOLUTION_FILENAME)

    @staticmethod
    def _get_last_timestamp() -> int:
        try:
            with open('.leetcode_last_timestamp', 'r') as file:
                return int(file.read())
        except FileNotFoundError:
            print("Last timestamp file not found. Initializing with default timestamp.")
            return 0

    @staticmethod
    def _update_last_timestamp(timestamp: int) -> None:
        with open('.leetcode_last_timestamp', 'w') as file:
            file.write(str(timestamp))

    def _generate_submission(self, path: str, submission: Dict[str, any]) -> None:
        content = self.solution_content_template.render(**submission)
        filename = self.solution_filename_template.render(**submission)
        with open(f"{path}/{filename}", 'w') as file:
            file.write(content)

    def _generate_question_readme(self, path: str, question: Dict[str, any]) -> None:
        content = self.readme_content_template.render(**question)
        with open(f"{path}/README.md", 'w') as file:
            file.write(content)

    def sync_recent_submissions(self) -> None:
        last_timestamp = self.last_timestamp

        for idx, submission in enumerate(self.parser.get_all_submissions(), 1):
            print(f"{idx} - submission id [{submission['id']}], question [{submission['title']}]")
            last_timestamp = max(last_timestamp, int(submission['timestamp']))

            # Check Language support
            if submission['lang'] not in constants.LANG_MAPPING:
                print(f'Unsupport format for submission: {submission}, skip')
                continue

            # Update submission info
            submission.update(constants.LANG_MAPPING.get(submission['lang']))
            submission['dt'] = datetime.datetime.fromtimestamp(int(submission['timestamp']))
            submission['question_id'] = int(submission['question_id'])

            # Create folder if it doesn't exist
            path = self.path_template.render(**submission)
            if not os.path.exists(path):
                os.makedirs(path)

            # Generate question README if it doesn't exist
            if not os.path.exists(f'{path}/README.md'):
                question = self.parser.get_question_info(submission['title_slug'])
                question['question_id'] = int(question.pop('questionId', 0))
                question['title_slug'] = question.pop('titleSlug', '')
                self._generate_question_readme(path, question)

            # Generate submission file
            self._generate_submission(path, submission)

        LeetcodeSync._update_last_timestamp(last_timestamp)


class LeetcodeParser:

    GRAPHQL_HOST: str = 'https://leetcode.com/graphql'
    API_HOST: str = 'https://leetcode.com/api'

    def __init__(
            self,
            csrf_token: str,
            leetcode_session: str,
            last_timestamp: int = 0,
        ) -> None:
        self.last_timestamp: int = last_timestamp
        self.headers: Dict[str, str] = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Cookie': f'LEETCODE_SESSION={leetcode_session};csrftoken={csrf_token}',
            'Referer': 'https://leetcode.com',
        }
        assert self.validate_session() is True

    def validate_session(self) -> bool:
        query = '''
            query {
              user {
                username
              }
            }
        '''
        resp = requests.post(self.GRAPHQL_HOST, headers=self.headers, timeout=5,
                             json={'query': query})
        if not resp.ok:
            print('Failed to validate session.')
            return False
        data = resp.json()
        if 'error' in data or not data['data']['user']:
            print('Session is not valid.')
            return False
        username = data['data']['user']['username']
        print(f'Session is valid. Logged in as: {username}')
        return True

    def get_all_submissions(self) -> Iterator[Dict[str, Any]]:
        """ Retrieves all accepted submissions that are newer than self.last_timestamp """
        last_key, offset, limit = '', 0, 20

        continue_looping = True
        while continue_looping:
            print(f'Retreving submissions, offset: {offset}')
            url = f'{self.API_HOST}/submissions/?lastkey={last_key}&offset={offset}&limit={limit}'
            resp = requests.get(url, headers=self.headers, timeout=5)
            if not resp.ok:
                print(f'Failed to get submissions: {resp.content}')
                time.sleep(random.random())
                continue

            data = resp.json()
            for submission in data['submissions_dump']:
                if submission['status_display'] != 'Accepted':
                    continue
                if int(submission['timestamp']) <= self.last_timestamp:
                    print(f'Timestamp: hit {self.last_timestamp}, stop')
                    continue_looping = False
                    break
                yield submission

            if not data.get('has_next', False):
                print('has_next is False, stop')
                continue_looping = False
                break
            last_key = data['last_key']
            offset += limit
            time.sleep(random.random())

    def get_all_questions(self, category_slug: str='all-code-essentials') -> Iterator[Dict[str, Any]]:
        """ Retrieves question list """
        query = constants.PROBLEMSET_QUESTION_LIST_QUERY
        offset, limit = 0, 20
        while True:
            print(f'Retreving questions for the problemset {category_slug}, offset: {offset}')
            variables =  {
                'categorySlug': category_slug,
                'filters': {},
                'limit': limit,
                'skip': offset,
            }
            resp = requests.post(self.GRAPHQL_HOST, headers=self.headers, timeout=5,
                                 json={'query': query, 'variables': variables})
            if not resp.ok:
                print(f'Failed to get questions: {resp.content}')
                time.sleep(random.random())
                continue

            data = resp.json()['data']['problemsetQuestionList']
            if not data['questions']:
                print('Got empty question list')
                break
            for question in data['questions']:
                yield question
            offset += limit
            time.sleep(random.random())

    def get_question_info(self, title_slug: str) -> Dict[str, Any]:
        """ Retrieves information about a question. """
        query = constants.QUESTION_INFO_QUERY
        variables = {
            'titleSlug': title_slug
        }
        resp = requests.post(self.GRAPHQL_HOST, headers=self.headers, timeout=5,
                             json={'query': query, 'variables': variables})
        if not resp.ok:
            print(f'Failed to get question detail: {resp.content}')
            return None
        return resp.json()['data']['question']

    def get_question_submission_list(self, title_slug: str) -> Iterator[Dict[str, Any]]:
        """ Retrieves a list of submissions for a given question. """
        query = constants.QUESTION_SUBMISSIONS_QUERY
        last_key, offset, limit = None, 0, 20
        while True:
            print(f'Retreving sumissions for the questions {title_slug}, offset: {offset}')
            variables =  {
                'questionSlug': title_slug,
                'lastKey': last_key,
                'limit': limit,
                'offset': offset,
                'status': 10,  # Accepted
            }
            resp = requests.post(self.GRAPHQL_HOST, headers=self.headers, timeout=5,
                                 json={'query': query, 'variables': variables})
            if not resp.ok:
                print(f'Failed to get submissions for the question: {resp.content}')
                time.sleep(random.random())
                continue

            data = resp.json()['data']['questionSubmissionList']
            if not data['submissions']:
                print('Got empty submission list')
                break
            for submission in data['submissions']:
                yield submission

            last_key = data.get('lastKey')
            if not data.get('hasNext', False):
                print('hasNext is False, stop')
                break
            offset += limit
            time.sleep(random.random())
