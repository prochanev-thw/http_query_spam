import asyncio
import aiohttp
import os
import logging
import datetime
import csv
import time
from concurrent.futures import ProcessPoolExecutor


from ..params import RequestParamsGenerator, create_request_params
from http_request_spam import utils, settings

TIMEOUT = settings.AppSettings.TIMEOUT_RESPONSE
COUNT_CONNECTIONS = settings.AppSettings.LIMIT_CONNECTION
COUNT_PARALLEL_TASKS = settings.AppSettings.LIMIT_SEMAPHORE
logger = logging.getLogger(__name__)

class SpamSession:
    def __init__(
        self,
        request_count: int,
        duration_in_seconds: int,
        use_proxy: bool,
        start_date
    ):
        self.request_count = request_count
        self.duration_in_seconds = duration_in_seconds
        self.use_proxy = use_proxy
        self.target_urls = utils.txt_to_list('http_request_spam/program_params/site_list.txt')
        self.request_params_generator = RequestParamsGenerator(
            'http_request_spam/program_params/proxies.txt',
            'http_request_spam/program_params/user_agent.txt',
            'http_request_spam/program_params/cookies.txt',
        )
        logger.info('Параметры запросов обновлены')
        self.start_date = start_date

    async def check_status_code(self, params, session, second_number, sem):
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        
        async with sem:
            try:
                async with session.get(**params, timeout=TIMEOUT, ssl=False) as response:
                    await response.read()
                    response_time = loop.time() - start_time
                    return (
                        params['url'],
                        params.get('proxy', 'localhost'),
                        response.status,
                        response_time,
                    )

            except aiohttp.client_exceptions.ClientError as exc:
                
                return (
                    params['url'],
                    params.get('proxy', 'localhost'),
                    str(exc),
                    '',
                )

            except asyncio.exceptions.TimeoutError as exc:
                return (
                    params['url'],
                    params.get('proxy', 'localhost'),
                    'timeout error',
                    '',
                )

    async def run_session(self, second_number):

        logger.info(f'''
            Старт сессии в процессе
            Количество запросов {self.request_count}
            Использование proxy {self.use_proxy}
            Целевые адреса {self.target_urls}
        ''')

        sem = asyncio.Semaphore(COUNT_PARALLEL_TASKS)
        connector = aiohttp.TCPConnector(limit=COUNT_CONNECTIONS)
        tasks = []

        params_portion = create_request_params(
            self.target_urls,
            self.request_params_generator,
            self.request_count,
            self.use_proxy
        )

        logger.info('Порция параметров балы сгенерирована')
        logger.info(f'Старт запросов в процессе')

        async with aiohttp.ClientSession(connector=connector) as session:
            for params in params_portion:
                task = asyncio.create_task(self.check_status_code(params, session, second_number, sem))
                task.add_done_callback(tasks.remove)
                tasks.append(task)
            logger.info(f'{self.request_count} задачь добавлены в цикл событий')

            logger.info(f"""
                Порция из {self.request_count} запросов отправлена
                для url {params['url']}
                start_date {self.start_date}
                duration {self.duration_in_seconds}'
            """)

            result = await asyncio.gather(*tasks)
            return result

    def run(self, second_number):
        
        logger.info(f'Запущена сессия в отдельном процессе')

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
        loop = asyncio.new_event_loop()
        logger.info('Цикл событий создан')
        result = loop.run_until_complete(self.run_session(second_number))
        loop.close()
        logger.info('Цикл событий закрыт')

        logger.info(f"""
            Старт записи в файл
            для start_date: {self.start_date}
            duration: {self.duration_in_seconds}
        """)

        with open(f'{self.start_date.replace(".", "-").replace(":", "_")} - second_number {second_number}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for r in result:
                writer.writerow(list(r))

        logger.info(f"""
            Данные по ответам записаны в файл
            для start_date: {self.start_date}
            duration: {self.duration_in_seconds}
        """)

    def run_processes(self):
        futures = []
        with ProcessPoolExecutor(self.duration_in_seconds) as pool:
            for second_number in range(1, self.duration_in_seconds + 1):
                future = pool.submit(self.run, second_number)
                futures.append(future)
                logger.info(f'Запущен процесс с порядковым номером {second_number}')
                time.sleep(1)

            for f in futures:
                if f.done():
                    continue

            logger.info('Сессия успешно окончена')
