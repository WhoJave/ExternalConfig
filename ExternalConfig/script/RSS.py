#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ssr_decode
import argparse
import os
import json
import socket
from os.path import expanduser
import re
from urllib import request

url = ""
#default port
port = 19522
home = expanduser("~")
surgePath = "/Documents/Surge/config"

def get_data(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
    req = request.Request(url, headers=header)
    with request.urlopen(req) as res:
        data = str(res.read(), encoding="utf-8")
        return data


# 解码订阅内容获得配置保存在目录config

def del_files(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".json"):
                os.remove(os.path.join(root, name))

def save_config(url, port):
    data = get_data(url)
    ssr_str = ssr_decode.decode(data)

    code_list = re.findall("ssr://(\w+)", ssr_str)
    
    if not os.path.exists(home + surgePath + '/SSRJson'):
        os.makedirs(home + surgePath + '/SSRJson')
    writepath = home + surgePath + '/external.txt'
    mode = 'a' if os.path.exists(writepath) else 'w'
    f = open(writepath, mode)
    f.truncate()
    f.close()
    for code in code_list:
        index = code_list.index(code)
        try:
#            print(code,index,port) #pass port
            ssr_decode.save_as_json(code, port, name=str(index))
        except UnicodeDecodeError:
            print(ssr_decode.decode(code))  # 打印有误的链接

def getIP(domain):
    try:
        myaddr = socket.gethostbyname(domain)
    except:
        myaddr = 'unknown'
    return myaddr

def configToExternal():
    rootdir = home + surgePath
    f = open(home + surgePath +'/external.txt','w+')
    f.truncate()
    f.close()
    for root, dirs, files in os.walk(rootdir + '/SSRJson'):  # 当前路径、子文件夹名称、文件列表
        for filename in files:
            if filename.endswith(".json"):
                fn = filename.split('.')[0]
#                print(fn)
                with open(rootdir + '/SSRJson' + '/' + filename, 'r') as f:
                    tmp = json.loads(f.read())
                    lp = tmp['local_port']
                    se = tmp['server']
                    serverIP = getIP(se)
#                    print(lp)
                    print(fn + ' = external, exec = \"'+ home + surgePath + '/ss-local\", args = \"-c\", args = \"' + rootdir + '/SSRJson' + '/' + filename + '\",' + 'local-port = ' + str(lp) + ', addresses = '+ serverIP)
                    f = open(rootdir + '/external.txt', 'a')
                    f.write(fn + ' = external, exec = \"'+ home + surgePath + '/ss-local\", args = \"-c\", args = \"' + rootdir + '/SSRJson' + '/' + filename + '\",' + 'local-port = ' + str(lp) + ', addresses = '+ serverIP +'\n')
                    f.close()
        nodeListStr = ''
        for filename in files:
            if filename.endswith(".json"):
                fn = filename.split('.')[0]
                nodeListStr = (nodeListStr +fn+',')
                f = open(rootdir + '/external.txt', 'a')
                f.write(nodeListStr)
                f.close()
        print(nodeListStr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s",help="this is the ssr subscribe address")
    parser.add_argument("-p",help="this is the destined port number")
    # parser.add_argument("-p","--port",help="this is the destined port number")
    args = parser.parse_args()
#    print('________打印参数________')
#    print(args)
    if args.s:
#        print(8,args.s)
        url = args.s
    if args.p:
        port = args.p
    
#    url = input("ssr subscrible link: ")
    del_files(home + surgePath + '/SSRJson')
    save_config(url, port)
    configToExternal()
#    print("successful!")
