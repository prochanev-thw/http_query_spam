import utils

def test_txt_to_dict():
    assert utils.txt_to_dict('tests/stub_cookies.txt') == {
        '_ym_uid':'1',
        '_ym_d':'2',
        '_ym_isad':'3',
    }

    assert utils.txt_to_dict('tests/stub_cookies_semicolon_sep.txt', row_sep='; ') == {
        '_ym_uid': '1624965576601325562',
        '_ym_d': '1624965576',
        '_ym_isad':'1',
    }

def test_txt_to_list():
    assert utils.txt_to_list('tests/stub_user_agent.txt') == [
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.34 Safari/537.36 Edg/83.0.478.25',
    ]

    assert utils.txt_to_list('tests/stub_proxies.txt') == [
        'bPp6GO:HqPssaU86N@194.35.113.97:3000',
        'bPp6GO:HqPssaU86N@109.248.129.212:3000',
        'bPp6GO:HqPssaU86N@46.8.192.37:3000',
        'bPp6GO:HqPssaU86N@45.15.73.123:3000',
        '203.202.245.58:80',
    ]
