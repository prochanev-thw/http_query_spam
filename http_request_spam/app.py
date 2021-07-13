import os
import datetime
import time
import multiprocessing as mp
import logging
import csv

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from http_request_spam.api.spam_session import SpamSession
from http_request_spam.settings import AppSettings
import http_request_spam.utils as utils

REQUEST_PER_SECONDS = AppSettings.REQUEST_PER_SECOND
USE_PROXY = AppSettings.USE_PROXY
SCHEDULE_FILE_PATH = AppSettings.SCHEDULE_FILE_PATH


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('apscheduler').setLevel(logging.ERROR)


def task(request_count, duration_in_seconds, use_proxy, start_date):
    spam_session = SpamSession(request_count, duration_in_seconds, use_proxy, start_date)
    spam_session.run()


def start(scheduler):

    schedule_items = [
        utils.parse_time(row) for 
        row in 
        utils.txt_to_list(SCHEDULE_FILE_PATH)
    ]

    logger.info('Будет запланировано %s заданий', len(schedule_items))

    for element in schedule_items:
        start_date = element['start_date']
        duration = element['duration']
        scheduler.add_job(
            task,
            'date',
            run_date=start_date,
            args=(
                REQUEST_PER_SECONDS,
                duration,
                USE_PROXY,
                start_date.strftime("%d.%m.%Y %H:%M:%S")
            ),
            executor='processpool'
        )
        logger.info(f'Задача с датой {start_date.strftime("%d.%m.%Y %H:%M:%S")} и продолжительностью {duration} запланирована')
    scheduler.start()
    return scheduler


if __name__ == '__main__':
    pool = ProcessPoolExecutor(3)
    scheduler = BackgroundScheduler(
        executors = {
            'processpool': pool
        },
        daemon=True
    )
    start(scheduler)
    logger.info('Планировщик задач запущен')
    try:
        # держим живым основной поток, который запускал планировщик
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        log_file_process.terminate()
        pool.terminate()
        scheduler.shutdown()
