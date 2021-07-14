class AppSettings:
    TIMEOUT_RESPONSE = 30
    REQUEST_PER_SECOND = 5_000
    USE_PROXY = False
    LIMIT_CONNECTION = 400
    LIMIT_SEMAPHORE = 5_000
    SCHEDULE_FILE_PATH = 'http_request_spam/program_params/time.txt'

class AppSettingsForOnce(AppSettings):
    TIMEOUT_RESPONSE = 20
    REQUEST_PER_SECOND = 5_000
    REQUEST_DURATION = 10
    USE_PROXY = False
