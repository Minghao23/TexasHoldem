# -*- encoding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import json

localhost = "127.0.0.1"
# host = "192.168.1.160"
host = localhost
port = "8000"


def test_join(name):
    url = "http://%s:%s/join" % (host, port)
    payload = {'name': name}
    response = requests.request("GET", url, params=payload)
    return response.text


def test_start():
    url = "http://%s:%s/start" % (host, port)
    response = requests.request("GET", url)
    return response.text


def test_check():
    url = "http://%s:%s/check" % (host, port)
    response = requests.request("GET", url)
    return response.text


def test_call():
    url = "http://%s:%s/call" % (host, port)
    response = requests.request("GET", url)
    return response.text


def test_raise(amount):
    url = "http://%s:%s/raise" % (host, port)
    payload = {'amount': amount}
    response = requests.request("GET", url, params=payload)
    return response.text


def test_fold():
    url = "http://%s:%s/fold" % (host, port)
    response = requests.request("GET", url)
    return response.text


def log(req, arg=None):
    if req == test_raise or req == test_join:
        text = req(arg)
    else:
        text = req()

    logs = json.loads(text)['log']
    for log in logs:
        print log


def info():
    url = "http://%s:%s/info" % (host, port)
    response = requests.request("GET", url)
    print response.text


# log(test_join, 'hmh')
# log(test_join, 'lvc')
# log(test_join, 'qk')
log(test_start)
#
# log(test_call)
# log(test_call)

# log(test_check)
# log(test_fold)
# log(test_raise, 30)

# info()