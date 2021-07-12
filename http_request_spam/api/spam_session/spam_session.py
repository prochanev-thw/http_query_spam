import asyncio
import aiohttp
import os
import logging
import datetime


from ..params import RequestParamsGenerator, create_request_params
from http_request_spam import utils, settings

TIMEOUT = settings.AppSettings.TIMEOUT_RESPONSE

logger = logging.getLogger(__name__)

class SpamSession:

    def __init__(
        self,
        request_count: int,
        duration_in_seconds: int,
        use_proxy: bool,
        queue,
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
        self.queue = queue
        self.start_date = start_date

    async def check_status_code(self, params, session, second_number):
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        try: 
            async with session.get(**params, timeout=TIMEOUT, ssl=False) as response:
                await response.read()
                response_time = loop.time() - start_time

                return (
                    params['url'],
                    params.get('proxy'),
                    response.status,
                    response_time,
                )

        except aiohttp.client_exceptions.ClientError as exc:
            return (
                    params['url'],
                    params.get('proxy'),
                    exc,
                    '',
                )

        except asyncio.exceptions.TimeoutError as exc:
            return (
                params['url'],
                params.get('proxy'),
                'timeout error',
                '',
            )

    
    async def run_session(self):
        logger.info('Старт сессии в процессе %d', os.getpid())
        connector = aiohttp.connector.TCPConnector(limit=self.request_count)
        session = aiohttp.ClientSession(connector=connector)
        tasks = []
        for second_number in range(1, self.duration_in_seconds + 1):
            params_portion = create_request_params(
                self.target_urls,
                self.request_params_generator,
                self.request_count,
                self.use_proxy
            )
            for params in params_portion:
                tasks.append(asyncio.create_task(self.check_status_code(params, session, second_number)))
                logger.info(f"Порция из {self.request_count} запросов отправлена для url {params['url']} start_date {self.start_date} duration {self.duration_in_seconds}'")
            await asyncio.sleep(1)
        results = await asyncio.gather(*tasks)
        await session.close()
        return results

    def run(self):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        result = asyncio.run(self.run_session())
        self.queue.put(
            {
                'start_date': self.start_date,
                'duration': self.duration_in_seconds,
                'response': result,
            }
        )
        logger.info(f'Данные по ответам записаны в файл для start_date: {self.start_date}, duration: {self.duration_in_seconds}')
