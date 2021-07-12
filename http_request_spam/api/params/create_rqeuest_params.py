from http_request_spam.api.params import request_params_generator


def create_request_params(
    target_urls: list,
    request_params_generator: request_params_generator.RequestParamsGenerator,
    query_count: int,
    use_proxy: bool
) -> list:
    """генерирует список праметров для отправки запроса

    Args:
        urls (list): список адресов, на которые нужно отправлять запросы
        request_params_generator (request_param_generator.RandomQueryParams): генерато случайныйх параметров для запроса
        query_count (int): количество запросов
        use_proxy (bool): используется ли прокси

    Returns:
        list: список параметров для запросов состоящий из url и рандомной части прокси, заголовков и куки
    """    
    result_params = []
    count_urls = len(target_urls)
    if use_proxy:
        request_params_generator.enable_proxy()
    else:
        request_params_generator.disable_proxy()
    request_count_per_url = int(query_count / count_urls)
    for url in target_urls:
        for _ in range(request_count_per_url):
            params = {'url': url}
            params.update(**request_params_generator())
            result_params.append(params)
    return result_params
