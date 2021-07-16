import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

import os
import datetime
import time
import multiprocessing as mp
import logging
import csv

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import apscheduler

from http_request_spam.api.spam_session import SpamSession
from http_request_spam.settings import AppSettings
import http_request_spam.utils as utils

REQUEST_PER_SECONDS = AppSettings.REQUEST_PER_SECOND
USE_PROXY = AppSettings.USE_PROXY
SCHEDULE_FILE_PATH = AppSettings.SCHEDULE_FILE_PATH


logging.basicConfig(
    level=logging.INFO,
    format='%(name)s:%(levelname)s - %(asctime)s процесс: %(process)s сообщение: %(message)s'
)

logger = logging.getLogger(__name__)
logging.getLogger('apscheduler').setLevel(logging.ERROR)

done_jobs = []

def my_listener(event):

    if event.exception:
        print('The job crashed :(')
    else:
        logger.info(f'Задание выполнено :), {event.job_id}')
        done_jobs.remove(event.job_id)
        logger.info(f'Оставшиеся задания {done_jobs}')
        if done_jobs:
            pass
        else:
            logger.info('-----------------Все запуски отработали, заданий больше нет--------------------')



def task(request_count, duration_in_seconds, use_proxy, start_date):
    spam_session = SpamSession(request_count, duration_in_seconds, use_proxy, start_date)
    
    logger.info(f'''
        Сессия запущена
        ----------------------------------
        количество запросов в секунду: {request_count},
        длительность: {duration_in_seconds}'
    ''')

    spam_session.run_processes()


def start(scheduler):

    schedule_items = [
        utils.parse_time(row) for 
        row in 
        utils.txt_to_list(SCHEDULE_FILE_PATH)
    ]

    scheduler.add_listener(
        my_listener,
        apscheduler.events.EVENT_JOB_EXECUTED | apscheduler.events.EVENT_JOB_EXECUTED
    )

    logger.info('Будет запланировано %s заданий', len(schedule_items))

    jobs = []
    for element in schedule_items:
        start_date = element['start_date']
        duration = element['duration']
        job = scheduler.add_job(
            task,
            'date',
            run_date=start_date,
            args=(
                REQUEST_PER_SECONDS,
                duration,
                USE_PROXY,
                start_date.strftime("%d.%m.%Y %H:%M:%S")
            )
            
        )
        jobs.append(job)
        done_jobs.append(job.id)
        logger.info(f'Задача с датой {start_date.strftime("%d.%m.%Y %H:%M:%S")} и продолжительностью {duration} запланирована')
    
    scheduler.start()
    return jobs


if __name__ == '__main__':
    pool = ThreadPoolExecutor(5)
    scheduler = BackgroundScheduler(
        executors={
            'default': pool
        },
        job_defaults = {
            'coalesce': False,
            'misfire_grace_time': 180
        }
    )
    jobs = start(scheduler)
    logger.info('Планировщик задач запущен')
    try:
        # держим живым основной поток, который запускал планировщик
        while True:
            if done_jobs:
                logger.info(f'Ожидание задачи')
                time.sleep(10)
            else:
                logger.info('Окончание работы программы')
                raise KeyboardInterrupt
    except (KeyboardInterrupt, SystemExit):
        pool.terminate()
        scheduler.shutdown()
