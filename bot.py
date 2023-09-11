import argparse
import time
import textwrap as tw

import requests
import telegram
from environs import Env


def main():
    env = Env()
    env.read_env()

    tg_token = env('TG_TOKEN')
    dvmn_token = env('DVMN_TOKEN')

    parser = argparse.ArgumentParser(
        description='Скрипт отправляет уведомление о проверке работ в указанный тг чат')
    parser.add_argument('chat_id',
                        help='укажите id своего телеграмм чата')
    args = parser.parse_args()

    bot = telegram.Bot(token=tg_token)
    chat_id = args.chat_id

    timestamp = None

    while True:
        url = 'https://dvmn.org/api/long_polling/'

        headers = {
            "Authorization": f'Token {dvmn_token}'
        }
        try:
            payload = {
                'timestamp': timestamp
            }
            raw_response = requests.get(
                url,
                headers=headers,
                params=payload,
                timeout=5)
            raw_response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            print('Ошибка соединения сети')
            time.sleep(10)
            continue

        dvmn_response = raw_response.json()

        if dvmn_response['status'] == 'timeout':
            timestamp = dvmn_response.get('timestamp_to_request')
            continue
        timestamp = dvmn_response.get('last_attempt_timestamp')

        new_attempts = dvmn_response['new_attempts']
        for attempt in new_attempts:
            if attempt['is_negative']:
                bot.send_message(chat_id=chat_id,
                                 text=tw.dedent(f'''
                                 У вас проверили работу "{attempt['lesson_title']}"\n
                                 Ссылка на урок - {attempt['lesson_url']}\n
                                 К сожалению в работе нашлись ошибки
                                    '''))
            else:
                bot.send_message(chat_id=chat_id,
                                 text=tw.dedent(f'''
                                 У вас проверили работу "{attempt['lesson_title']}"\n
                                 Ссылка на урок - {attempt['lesson_url']}\n
                                 Преподавателю все понравилось, можно приступать 
                                 к следующему уроку!
                                    '''))


if __name__ == '__main__':
    main()
