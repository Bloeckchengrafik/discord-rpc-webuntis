import requests
import webuntis


def otp_login(scname: str, server: str, token: str, username: str, time: int):
    url = server + '/WebUntis/jsonrpc_intern.do'
    headers = {'Content-Type': 'application/json'}
    data = {
        'id': 'Awesome',
        'method': 'getUserData2017',
        'params': [
            {
                'auth': {
                    'clientTime': time,
                    'user': username,
                    'otp': token,
                },
            },
        ],
        'jsonrpc': '2.0',
    }
    params = {
        'm': 'getUserData2017',
        'school': scname,
        'v': 'i2.2',
    }
    response = requests.post(url, json=data, headers=headers, params=params)
    s = webuntis.Session()
    if 'set-cookie' in response.headers:
        cookie_parts = response.headers['set-cookie'].split('; ')
        for part in cookie_parts:
            if part.startswith('JSESSIONID='):
                jsessionid = part[len('JSESSIONID='):]
                s.config['jsessionid'] = jsessionid
                s.config['username'] = username
                s.config['school'] = scname
                s.config['server'] = server
                s.config['useragent'] = 'WebUntis Test'
                break
    return s

