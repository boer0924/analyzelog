#!/usr/bin/python
# coding=utf-8
import json
from collections import Counter # Python2.7 feature
# import re
count = []
counter = {}
with open('./access.log', 'r') as f:
    for lines in f:
        lines.replace('\\x', '\\\\x')
        results = json.loads(lines)
        if results['http_x_forwarded_for'].decode('utf-8').find(',') != -1:
            if results['http_x_forwarded_for'].startswith(('192.168', '10.', '172.16')):
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