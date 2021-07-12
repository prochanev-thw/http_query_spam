import random
from http_request_spam import utils


class RequestParamsGenerator:
    """
       Получает в конструктор файлы с прокси, куки, юзер-агентами
       после инициализации можно получать случайный набор параметров для запроса

       enable_proxy() - включает прокси, по умолчанию включено
       disable_proxy() - отключает прокси
       refresh_files() - обновление списков с параметрами из файлов
       generate() - генерирует случайные параметры

    """

    def __init__(self, proxies_file_path, user_agent_file_path, cookies_file_path):

        self._proxies = None
        self._user_agent = None
        self._cookies = None

        self.proxies_file_path = proxies_file_path
        self.user_agent_file_path = user_agent_file_path
        self.cookies_file_path = cookies_file_path

        self.refresh_params_files()
        self.use_proxy = True
    
    def refresh_params_files(self):
        self._proxies = utils.txt_to_list(self.proxies_file_path)
        self._user_agent = utils.txt_to_list(self.user_agent_file_path)
        self._cookies = utils.txt_to_dict(self.cookies_file_path, row_sep='; ')
    
    def enable_proxy(self):
        self.use_proxy = True

    def disable_proxy(self):
        self.use_proxy = False

    def _random_referer(self) -> str:
        """Получение '', 'https://google.com', 'https://yandex.ru' с вероятностью 80%, 15%, 5% соотвественно

        Returns:
            str: строка полученная в соотвествии с вероятностью
        """    
        return random.choices(['', 'https://google.com', 'https://yandex.ru'], weights=[80, 15, 5])[0]

    def _random_proxy_url(self) -> str:
        return 'http://' + random.choice(self._proxies)

    def _random_cookies(self) -> dict:
        key = random.choice(list(self._cookies.keys()))
        return {key: self._cookies[key]}

    def _random_headers(self) -> str:

        headers_result = {
            'User-Agent': random.choice(self._user_agent)
        }

        referer = self._random_referer()

        if referer:
            headers_result['REFERER'] = referer

        return headers_result

    def __call__(self) -> dict:
        """
        возвращает словарь со случайными proxy_url, headers, cookies

        Returns:
            dict: словарь со случайными proxy_url, headers, cookies
        """

        params_result = {
            'headers': self._random_headers(),
            'cookies': self._random_cookies(),
        }

        if self.use_proxy:
            params_result['proxy'] = self._random_proxy_url()

        return params_result
