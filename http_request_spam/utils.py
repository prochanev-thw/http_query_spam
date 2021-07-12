import random
import datetime


def txt_to_dict(path_to_txt_file: str, sep: str='=', row_sep: str='\n') -> dict:
    """Преобразование строк текстового файла в словарь

    Args:
        path_to_txt_file (str): путь до текстового файла
        sep (str, optional): разделитель между ключем и значением. Defaults to '='.
        row_sep (str, optional) разделитель между строками. Defaults to '\n'.

    Returns:
        dict: словарь с ключами и значениями из текстового файла
    """

    result_dict = {}

    with open(path_to_txt_file, 'r') as f:
        for line in f.read().split(sep=row_sep):
            key, value = line.split(sep=sep)
            result_dict[key] = value
    
    return result_dict

def txt_to_list(path_to_txt_file: str) -> list:
    """преобразование текстового файла в список по разделителю '/n'

    Args:
        path_to_txt_file (str): путь до текстового файла

    Returns:
        list: строки файла преобразованные в список
    """    
    with open(path_to_txt_file, 'r') as f:
        return list(filter(lambda x: x if x != '' else False, f.read().split('\n')))

def parse_time(date_time_duration):

    date_value, time_value, duration_value = date_time_duration.split(';')
    datetime_string = f'{date_value} {time_value}'

    try:
        date_part = datetime.datetime.strptime(datetime_string, '%d.%m.%Y %H:%M:%S')
    except ValueError:
        raise Exception('Неверный формат даты, требуется "%d.%m.%Y %H:%M:%S"')

    try:
        duration_part = int(duration_value)
    except TypeError:
        raise Exception('Неверный формат продолжительности, требуется целое число')

    return {
        'start_date': date_part,
        'duration': duration_part,
    }
