#!venv/bin/python
# coding=utf-8
import json
from collections import Counter  # Python2.7 feature
import os
import paramiko as ssh

# 'sudo apt install libssl-dev libffi-dev python-dev'

client = ssh.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(ssh.AutoAddPolicy())
client.connect('127.0.0.1', 22, 'boer', os.environ.get('SSH_PASSWD'))
# stdin, stdout, stderr = client.exec_command('ls -l /home/boer')
# export SSH_PASSWD = '123456'

t = client.get_transport()
channel = t.open_session()
channel.exec_command('sudo cp /var/log/nginx/access.log /tmp/access.log && sudo chown app. /tmp/access.log')
exit_code = channel.recv_exit_status()
if exit_code == 0:
    ftp = client.open_sftp()
    remotepath = '/tmp/access.log'
    localpath = '/tmp/access.log-' + host
    ftp.get(remotepath, localpath)
    ftp.close()
    t.close()
    client.close()
else:
    print 'remote command error'
    t.close()
    client.close()
    sys.exit()


count = []
counter = {}
with open('./access.log', 'r') as f:
    for lines in f:
        lines.replace('\\x', '\\\\x')
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
        count.append(custom_ip)
        if custom_ip in counter:
            counter[custom_ip] += 1
        else:
            counter[custom_ip] = 1

for item in Counter(count).most_common(10):
    print item
print '=' * 50
flag = 0
for item in sorted(counter.items(), key=lambda d: d[1], reverse=True):
    print item
    flag += 1
    if flag == 10:
        break
