import requests
import pytz
from datetime import datetime


def get_attempt_time(attempt_record):
    student_tz = pytz.timezone(attempt_record['timezone'])
    utc_dt = datetime.utcfromtimestamp(attempt_record['timestamp'])
    return student_tz.localize(utc_dt)


def get_page_with_attempts(api_url, payload):
    response = requests.get(api_url, payload)
    return response.json()


def get_attempts_and_next_page(api_url, page):
    attempts = get_page_with_attempts(api_url, {'page': page})
    is_next_page = attempts['page'] < attempts['number_of_pages']
    return is_next_page, attempts['records']


def load_attempts(api_url):
    page = 1
    is_next_page = True

    while is_next_page:
        is_next_page, attempt_records = get_attempts_and_next_page(api_url,
                                                                   page)
        page += 1
        for record in attempt_records:
            if record['timestamp']:
                yield record


def get_midnighters(attempt_records):
    midnighters = {}
    min_hour = 0
    max_hour = 5

    for record in attempt_records:
        attempt_time = get_attempt_time(record)
        if attempt_time.hour in range(min_hour, max_hour):
            midnighters.setdefault(record['username'],
                                   []).append(attempt_time)
    return midnighters


def main():
    api_url = 'http://devman.org/api/challenges/solution_attempts/'
    output = "User {user} sent a night solution " \
             "last time at {last_time}"
    for user, dates in get_midnighters(load_attempts(api_url)).items():
        last_time = max(dates).strftime('%d-%m-%Y %H-%M-%S %Z')
        fmt_params = {'user': user, 'last_time': last_time}
        print(output.format(**fmt_params))


if __name__ == '__main__':
    main()
