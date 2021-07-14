import os
import pathlib


import datetime
import multiprocessing as mp
import logging

from http_request_spam.api.spam_session import SpamSession
from http_request_spam.settings import AppSettingsForOnce
import http_request_spam.utils as utils

REQUEST_PER_SECONDS = AppSettingsForOnce.REQUEST_PER_SECOND
REQUEST_DURATION = AppSettingsForOnce.REQUEST_DURATION
USE_PROXY = AppSettingsForOnce.USE_PROXY
START_DATE = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")


logging.basicConfig(
    level=logging.INFO,
    format='%(name)s:%(levelname)s - %(asctime)s процесс: %(process)s сообщение: %(message)s'
)
logger = logging.getLogger(__name__)

def task(request_count, duration_in_seconds, use_proxy, start_date):
    spam_session = SpamSession(request_count, duration_in_seconds, use_proxy, start_date)
    
    logger.info(f'''
        Сессия запущена
        ----------------------------------
        количество запросов в секунду: {request_count},
        длительность: {duration_in_seconds}'
    ''')

    spam_session.run_processes()

if __name__ == '__main__':
    process = mp.Process(
        target=task,
        args=(
            REQUEST_PER_SECONDS,
            REQUEST_DURATION,
            USE_PROXY,
            START_DATE,
        )
    )

    logger.info(f'Старт отправки запросов, будет создано {REQUEST_DURATION} дочерних процессов')
    process.start()
    logger.info(f'Ожидание окончания отправки запросов')
    process.join()
