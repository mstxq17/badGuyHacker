#!/usr/bin/python3
# -*- coding:utf-8 -*-

import gevent
from gevent import monkey; monkey.patch_all()
from multiprocessing import Process, Manager
import paramiko, pysnooper, time

# @pysnooper.snoop("sshPwndebug.log")
# @pysnooper.snoop()
def ssh(ip, username, password, cmd, stdinput="", port=22):
    # 创建 ssh客户端
    client = paramiko.SSHClient()
    try:
        # 第一次ssh远程时会提示输入yes或者no
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 通过密码的方式连接
        client.connect(ip, port, username=username, password=password, timeout=3)
        # 是否启用交互
        if stdinput:
            # 启用交互模式来执行
            chan = client.invoke_shell()
            chan.send(cmd + "\n")
            time.sleep(0.2)
            for char in stdinput.split("\n"):
                char = char.strip()
                chan.send(char + '\n')
                time.sleep(0.2)
            result = chan.recv(2048).decode()
            chan.send("exit(0)" + "\n")
            chan.close()
            return result[result.find(cmd):]
        else:
            # 尝试执行非交互命令
            stdin, stdout, stderr = client.exec_command(cmd)
            #获取命令执行结果
            cmd_result = stdout.read().decode(), stderr.read().decode()
            #返回执行结果
            return cmd_result

    except paramiko.AuthenticationException as error:
        print("[-]ssh Login Error! password or username not correct!")
        return ('', '')

    except Exception as e:
        print("[-]ssh Fail! Exception Error!")
        return ('', '')

    finally:
        # 关闭客户端
        client.close()


# @pysnooper.snoop()
def change_pass(ip, username, user, oldpass, newpass, port=22):
    # root 权限下快速更改密码
    cmd = "echo {user}:{password} | chpasswd".format(user=user, password=newpass)
    stdout, stderr = ssh(ip, username, oldpass, cmd, "", port)
    # 说明当前权限不对, 那么就尝试使用passwd命令来修改当前用户的密码
    if 'Authentication token manipulation error' in stderr:
        print("[-] change_pass ! chpasswd Fail not root, try passwd...")
        cmd = "passwd"
        stdinput = "{oldpass}\n{password}\n{password}".format(oldpass=oldpass, password=newpass)
        res = ssh(ip, username, oldpass, cmd, stdinput, 22)
        if 'password updated successfully' in res:
            print("[+]change_pass Success! ")
            return True
        else:
            # 这里因为有可能密码和原来密码一致
            if oldpass == newpass:
                print("[-]change_pass Fail!  oldpass equals newpass!")
            else:
                print("[-]change_pass Fail! unpredictable Error!")
            return False
    elif not stdout:
        print("[-]change_pass Fail!")
        return False


def add_user(ip, username, password, user, userpass, port=22):
    cmd = "adduser {user}".format(user=user)
    stdinput = "{password}\n{password}\n\n\n\n\n".format(password=password)
    output = ssh(ip, username, password, cmd, stdinput, port)
    if "password updated successfully" in output:
        print("[+] add_user Success:{ip}:{username}:{password}".format(ip=ip, username=username, password=password))
        return True
    else:
        print("[-] add_user Failed!")
        return False


def main():
    ip = 'xxxxx'
    port = 22
    username = 'test000'
    # password = 'xxxxx'
    password = 'test1111'
    add_user(ip, username, password, 'test000111', password)
    change_pass(ip, username, 'test000', password, 'test11112', 22)

if __name__ == '__main__':
    main()