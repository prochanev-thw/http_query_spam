# http_query_spam
Программа для отправки большого числа запросов на определенные URL адреса. Для стресс проверки вашего сервера.

Настройки в файле `http_request_spam/program_params/time.txt`  
Так же настройки есть в файле `http_request_spam/settings.py` есть настройки  

    TIMEOUT_RESPONSE = 15
    REQUEST_PER_SECOND = 15_000
    USE_PROXY = False
    SCHEDULE_FILE_PATH = 'http_request_spam/program_params/time.txt'

Для установки и запуска нужно:

1. активировать виртуальное окружение
2. запустить `pip install -r requirements.txt`
3. Для запуска `python -m http_request_spam.app`

---
Предварительно не забыть установить время запуска и длительность сессии в файле `time.txt`

Для остановки программ `CTRL + C`