#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = 'boer'

import json
import re
import os
import sys
from multiprocessing import Process, Pool
import paramiko as ssh

# 'sudo apt install libssl-dev libffi-dev python-dev'

def red_text(txt):
    return '\033[31m' + txt + '\033[0m'

def green_text(txt):
    return '\033[32m' + txt + '\033[0m'

def get_log(host):
    'ftp web服务器nginx日志.'
    client = ssh.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(ssh.AutoAddPolicy())
    client.connect(host, 22, 'app')

    t = client.get_transport()
    channel = t.open_session()
    channel.get_pty()
    channel.exec_command('sudo cp -f /var/log/nginx/access.log /tmp/access.log && sudo chown app. /tmp/access.log')
    print '...', channel.recv(9999)
    print '...', channel.recv_stderr(9999)

    ftp = client.open_sftp()
    remotepath = '/tmp/access.log'
    localpath = '/tmp/access.log-' + host
    ftp.get(remotepath, localpath)
    ftp.close()

    t.close()
    client.close()


def analyze_log(logfile):
    'analyze单台服务器日志.'
    counter = {}
    with open(logfile, 'r') as f:
        for lines in f:
            lines = re.sub(r'\\', r'\\\\', lines)
            results = json.loads(lines)
            # real client IP.
            if results['http_x_forwarded_for'].decode('utf-8').find(',') != -1:
                if results['http_x_forwarded_for'].startswith(
                    ('192.168', '10.', '172.16')):
                    custom_ip = results['http_x_forwarded_for'].split(',')[1]
                else:
                    custom_ip = results['http_x_forwarded_for'].split(',')[0]
            else:
                if results['http_x_forwarded_for'] != '-':
                    custom_ip = results['http_x_forwarded_for']
            # bad request or response log.
            if results['status'].decode('utf-8') in ['400']:
                with open('/tmp/bad_log.log', 'a') as log:
                    log.write(lines)
            # counter IP
            if custom_ip in counter:
                counter[custom_ip] += 1
            else:
                counter[custom_ip] = 1

    return counter


def exec_get_log(hosts):
    'multiprocessing 获取多台服务器日志.'
    p = Pool(len(hosts))
    for host in hosts:
        p.apply_async(get_log, args=(host,))
        print red_text('Get log file done.by'), green_text(host)
    p.close()
    p.join()
    print green_text('Get all log done...')


#def exec_analyze(logfiles):
#    p = Pool(len(logfiles))
#    results = []
#    for logfile in logfiles:
#        results.append(p.apply_async(analyze_log, args=(logfile,)).get())
#        print red_text(logfile), green_text('analyze done...')
#    p.close()
#    p.join()
#    return results


if __name__ == '__main__':
    # prod web server
    hosts = ['192.168.28.12', '192.168.28.13']
    # testing web server
    # hosts = ['172.19.3.24', '172.19.3.25']
    logfiles = ['/tmp/access.log-' + host for host in hosts]

    # 调用多进程获取日志函数
    exec_get_log(hosts)
    
    counter = {}
    # multiprocessing Pool对象的map函数用法.
    p = Pool(len(logfiles))
    results = p.map(analyze_log, logfiles)
    for item in results:
        for k, v in item.items():
            if k in counter:
                counter[k] += v
            else:
                counter[k] = v

    print 'Start results'.center(60, '*')
    flag = 0
    # 根据dict值排序输出
    for item in sorted(counter.items(), key=lambda d: d[1], reverse=True):
        print red_text(item[0]), '=>', green_text(str(item[1]))
        flag += 1
        if flag == 20:
            break
    print 'End results'.center(60, '*')
