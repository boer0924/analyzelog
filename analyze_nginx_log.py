#!venv/bin/python
# coding=utf-8
import json
import re
import os
import sys
import time
# import paramiko as ssh
from multiprocessing import Pool

# 'sudo apt install libssl-dev libffi-dev python-dev'


# def get_log(host):
#     client = ssh.SSHClient()
#     client.load_system_host_keys()
#     client.set_missing_host_key_policy(ssh.AutoAddPolicy())
#     client.connect(host, 22, 'boer', os.environ.get('SSH_PASSWD'))
#     stdin, stdout, stderr = client.exec_command('')
#     # export SSH_PASSWD = '123456'

#     t = client.get_transport()
#     channel = t.open_session()
#     channel.exec_command(
#         'sudo cp /var/log/nginx/access.log /tmp/access.log && sudo chown app. /tmp/access.log')
#     exit_code = channel.recv_exit_status()
#     if exit_code == 0:
#         ftp = client.open_sftp()
#         remotepath = '/tmp/access.log'
#         localpath = '/tmp/access.log-' + host
#         ftp.get(remotepath, localpath)
#         ftp.close()
#         t.close()
#         client.close()
#     else:
#         print 'remote command error'
#         t.close()
#         client.close()
#         sys.exit()
#     return


def analyze_log(logfile):
    start = time.time()
    print 'Current log %s, -> pid [%s]' % (logfile, os.getpid())
    # count = []
    counter = {}
    with open(logfile, 'r') as f:
        for lines in f:
            # lines = re.sub(r'\\', r'\\\\', lines)
            # lines = lines.replace('\\', '\\\\')
            results = json.loads(lines)
            if results['http_x_forwarded_for'].decode('utf-8').find(',') != -1:
                if results['http_x_forwarded_for'].startswith(
                    ('192.168', '10.', '172.16')):
                    custom_ip = results['http_x_forwarded_for'].split(',')[1]
                else:
                    custom_ip = results['http_x_forwarded_for'].split(',')[0]
            else:
                if results['http_x_forwarded_for'] != '-':
                    custom_ip = results['http_x_forwarded_for']
            # count.append(custom_ip)
            if custom_ip in counter:
                counter[custom_ip] += 1
            else:
                counter[custom_ip] = 1
    end = time.time()
    print '共用时：', (end - start)
    print '=' * 50
    return counter


def exec_analyze(logfiles):
    results = []
    p = Pool(len(logfiles))
    for logfile in logfiles:
        results.append(p.apply_async(analyze_log, args=(logfile,)).get())
    p.close()
    p.join()
    return results

if __name__ == '__main__':
    hosts = ['192.168.28.12', '192.168.28.13']
    logfiles = ['./access.log-' + host for host in hosts]
    counter = {}

    print 'Start results'.center(60, '=')

    for item in exec_analyze(logfiles):
        for k, v in item.items():
            if k in counter:
                counter[k] += v
            else:
                counter[k] = v

    flag = 0
    for item in sorted(counter.items(), key=lambda d: d[1], reverse=True):
        print item
        flag += 1
        if flag == 5:
            break

    print 'End results'.center(60, '=')
