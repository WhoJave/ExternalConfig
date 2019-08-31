#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import re
import json
import os
from os.path import expanduser

ssr = "ssr://"
code = ssr[6:]
name = 'config'
surgePath = "/Documents/Surge/config"

#功能：解析我们的ssr code 返回一个有config,group,remarks组成的列表,
#参数：s为去掉了前缀'ssr://'的ssr链接code，类型为string
#返回：[config,group,remarks],其中config，类型为dict；group和remarks，类型为string
def Analyze(s,port):

    config = {
        "server": "0.0.0.0",
        "server_ipv6": "::",
        "server_port": 8388,
        "local_address": "127.0.0.1",
        "local_port": port,

        "password": "m",
        "method": "aes-128-ctr",
        "protocol": "auth_aes128_md5",
        "protocol_param": "",
        "obfs": "tls1.2_ticket_auth_compatible",
        "obfs_param": ""
    }

    s = decode(s)
    spilted = re.split(':', s)
    pass_param = spilted[5]
    pass_param_spilted = re.split("\/\?", pass_param)
    passwd = decode(pass_param_spilted[0])

    #匹配param、remark和group 
    try:
        obfs_param = re.search(r'obfsparam=([^&]+)', pass_param_spilted[1]).group(1)
        obfs_param = decode(obfs_param)
    except:
        obfs_param = ''
    try:
        protocol_param = re.search(r'protoparam=([^&]+)', pass_param_spilted[1])
        protocol_param = decode(protocol_param)
    except:
        protocol_param = ''
    try:
        remarks = re.search(r'remarks=([^&]+)', pass_param_spilted[1]).group(1)
        remarks = decode(remarks)
    except:
        remarks = ''
    try:
        group = re.search(r'group=([^&]+)', pass_param_spilted[1]).group(1)
        group = decode(group)
    except:
        group = ''

    config['server'] = spilted[0]
    config['server_port'] = int(spilted[1])
    config['password'] = passwd
    config['method'] = spilted[3]
    config['protocol'] = spilted[2]
    config['obfs'] = spilted[4]
    config['protocol_param'] = protocol_param
    config['obfs_param'] = obfs_param
    
    return [config,group,remarks]

#功能：Base64解码(针对url)    
#参数：待解码的字符串s，类型为string
#返回：解码后的内容，类型为string
def decode(s):

    count = len(s)
    num = 4-count%4
    if count%4==0:
        s = base64.urlsafe_b64decode(s)
    else:
        s = s + num*"="
        s = base64.urlsafe_b64decode(s)
    
    s = str(s,encoding="utf-8")
    return s

#功能：解析ssr并保存在config目录下
#参数：d为去掉'ssr://'前缀，name为保存的config的名字默认为conf
def save_as_json(d,port,name='conf'):
#    print(d)
#    print('***********')
    [data_dict,group,remarks] = Analyze(d,port)
    #修改local端口号
    data_dict['local_port'] = int(data_dict['local_port']) + int(name)
    json_str = json.dumps(data_dict)
    home = expanduser("~")
    if not os.path.exists(home + surgePath + '/SSRJson'):
        os.makedirs(home + surgePath + '/SSRJson')
    with open(home + surgePath + '/SSRJson' + '/' + remarks + '.json', 'w') as f:
        json.dump(data_dict, f)

#从终端输入ssr链接，将解析后的配置保存到目录config下
if __name__ == "__main__":
    ssr = input('ssr link:')
    code = ssr[6:]
    name = input('config name:')
    try:
#        print(code)
#        print(name)
#        save_as_json(code,port,name)
        print("Successful:please check config at \'config/\'")
    except:
        print("Error:Fail to save config!")
