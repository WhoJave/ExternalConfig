#!/usr/bin/env python3
import os
import sys
import json
import base64
import argparse
import binascii
import traceback
import urllib.request
import urllib.parse
import socket
from os.path import expanduser

vmscheme = "vmess://"
ssscheme = "ss://"

home = expanduser("~")
surgePath = "/Documents/Surge/config/vmessJson"

TPL = {}
TPL["CLIENT"] = """
{
    "log": {
        "loglevel": "info"
    },
    "inbound": {
        "listen": "127.0.0.1",
        "port": 11098,
        "protocol": "socks",
        "settings": {
            "auth": "noauth",
            "udp": true,
            "ip": "127.0.0.1"
        }
    },
    "outbound": {
        "protocol": "vmess",
        "settings": {
            "vnext": [
                {
                    "address": "v2-hk5.54dywr.com",
                    "port": 543,
                    "users": [
                        {
                            "id": "15fa756f-8fc6-3be5-93e3-24094d5fbb8a",
                            "alterId": 2
                        }
                    ]
                }
            ]
        }
    }
}
"""


def parseLink(link):
    if link.startswith(ssscheme):
        return parseSs(link)
    elif link.startswith(vmscheme):
        return parseVmess(link)
    else:
        print("ERROR: This script supports only vmess://(N/NG) and ss:// links")
        return None


def parseSs(sslink):
    RETOBJ = {
        "v": "2",
        "ps": "",
        "add": "",
        "port": "",
        "id": "",
        "aid": "",
        "net": "shadowsocks",
        "type": "",
        "host": "",
        "path": "",
        "tls": ""
    }
    if sslink.startswith(ssscheme):
        info = sslink[len(ssscheme):]

        if info.rfind("#") > 0:
            info, _ps = info.split("#", 2)
            RETOBJ["ps"] = urllib.parse.unquote(_ps)

        if info.find("@") < 0:
            # old style link
            # paddings
            blen = len(info)
            if blen % 4 > 0:
                info += "=" * (4 - blen % 4)

            info = base64.b64decode(info).decode()

            atidx = info.rfind("@")
            method, password = info[:atidx].split(":", 2)
            addr, port = info[atidx + 1:].split(":", 2)
        else:
            atidx = info.rfind("@")
            addr, port = info[atidx + 1:].split(":", 2)

            info = info[:atidx]
            blen = len(info)
            if blen % 4 > 0:
                info += "=" * (4 - blen % 4)

            info = base64.b64decode(info).decode()
            method, password = info.split(":", 2)

        RETOBJ["add"] = addr
        RETOBJ["port"] = port
        RETOBJ["aid"] = method
        RETOBJ["id"] = password
        return RETOBJ


def parseVmess(vmesslink):
    """
    return:
{
  "v": "2",
  "ps": "remark",
  "add": "4.3.2.1",
  "port": "1024",
  "id": "xxx",
  "aid": "64",
  "net": "tcp",
  "type": "none",
  "host": "",
  "path": "",
  "tls": ""
}
    """
    if vmesslink.startswith(vmscheme):
        bs = vmesslink[len(vmscheme):]
        # paddings
        blen = len(bs)
        if blen % 4 > 0:
            bs += "=" * (4 - blen % 4)

        vms = base64.b64decode(bs).decode()
        return json.loads(vms)
    else:
        raise Exception("vmess link invalid")


def load_TPL(stype):
    s = TPL[stype]
    return json.loads(s)


def fill_basic(_c, _v):
    _outbound = _c["outbound"]
    _vnext = _outbound["settings"]["vnext"][0]
    # address为服务器域名 后续需要获取IP
    _vnext["address"] = _v["add"]
    _vnext["port"] = int(_v["port"])
    _vnext["users"][0]["id"] = _v["id"]
    _vnext["users"][0]["alterId"] = int(_v["aid"])

    return _c


def vmess2client(_t, _v):
    _net = _v["net"]
    _type = _v["type"]
    # print(_t)
    # print('***************')
    # print(_v)
    _c = fill_basic(_t, _v)

    return _c


def read_subscribe(sub_url):
    print("Reading from subscribe ...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = urllib.request.Request(url=sub_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        _subs = response.read()
        return base64.b64decode(_subs + b'=' * (-len(_subs) % 4)).decode().splitlines()


def jsonDump(obj, fobj):
    if option.update is not None:
        oconf = json.load(option.update)
        if "outbound" not in oconf:
            raise KeyError("outbound not found in {}".format(option.update.name))

        oconf["outbound"] = obj["outbound"]
        option.update.close()
        with open(option.update.name, 'w') as f:
            json.dump(oconf, f, indent=4)
        print("Updated")
        return

    if option.outbound:
        json.dump(obj['outbound'], fobj, indent=4)
    else:
        json.dump(obj, fobj, indent=4)


def select_multiple(lines, myPort):
    vmesses = []
    vmessNames = []
    for _v in lines:
        _vinfo = parseLink(_v)
        if _vinfo is not None:
            # - { name: "", type: vmess, server: ***.com, port: ***, uuid: ***, alterId: 2, cipher: none }
            # vmesses.append({ "ps": "[{ps}] {add}:{port}/{net}/{id}/{aid}".format(**_vinfo), "vm": _v })
            vmesses.append({"ps": "- {{ name: \"{ps}\",type: vmess, server: {add}, port: {port}, uuid: {id}, alterId: {aid}, cipher: none }}".format(**_vinfo), "vm": _v})
            vmessNames.append({"name": "{ps}".format(**_vinfo)})

    print("Found {} items.".format(len(vmesses)))
    f = open(home + surgePath + '/vmessClash.txt', 'w')
    f.truncate()
    f.close()
    f = open(home + surgePath + '/v2rayExternal.txt', 'w')
    f.truncate()
    f.close()
    for i, item in enumerate(vmesses):
        # print("[{}] - {}".format(i+1, item["ps"]))
        # print("{}".format(item["ps"]))
        f = open(home + surgePath + '/vmessClash.txt', 'a')
        f.write("{}\n".format(item["ps"]))
        f.close()

        remarks = vmessNames[i]['name']
        # print(remarks)
        ln = parseLink(item['vm'])
        if ln is None:
            return
        cc = (vmess2client(load_TPL("CLIENT"), ln))
        cc['inbound']['port'] = int(myPort) + i
        lp = cc['inbound']['port']
        serverIP = getIP(cc['outbound']['settings']['vnext'][0]['address'])
        if not os.path.exists(home + surgePath):
            os.makedirs(home + surgePath)
        writepath = home + surgePath + '/' + remarks + '.json'
        print(
            remarks + ' = external, exec = \"' + home + '/Documents/Surge/config/v2raycore/v2ray\", args = \"' + '--config=' + home + surgePath + '/' + remarks + '.json' + '\", ' + 'local-port = ' + str(
                lp) + ', addresses = ' + '\"' + serverIP + '\"')
        f = open(home + surgePath + '/v2rayExternal.txt', 'a')
        f.write(
            remarks + ' = external, exec = \"' + home + '/Documents/Surge/config/v2raycore/v2ray\", args = \"' + '--config=' + home + surgePath + '/' + remarks + '.json' + '\", ' + 'local-port = ' + str(
                lp) + ', addresses = ' + '\"' + serverIP + '\"' + '\n')
        f.close()
        if os.path.exists(writepath):
            # mode = 'a' if os.path.exists(writepath) else 'w'
            with open(writepath, 'w') as f:
                json.dump(cc, f, indent=4)
        else:
            with open(writepath, 'w') as f:
                json.dump(cc, f, indent=4)

        # with open(writepath, mode) as f:
        #         json.dumps(cc, f, indent=4)

    # print(vmessNames)
    for i, item in enumerate(vmessNames):
        f = open(home + surgePath + '/vmessClash.txt', 'a')
        f.write(item['name'])
        print(item['name'] + ',')
        if i != len(vmessNames) - 1:
            f.write(',')
        f.close()


def detect_stdin():
    if sys.stdin.isatty():
        return None
    stdindata = sys.stdin.read()
    try:
        lines = base64.b64decode(stdindata).decode().splitlines()
        option.subscribe = "-"
        return lines
    except (binascii.Error, UnicodeDecodeError):
        return stdindata.splitlines()


def getIP(domain):
    try:
        myaddr = socket.gethostbyname(domain)
    except BaseException:
        myaddr = 'unknown'
    return myaddr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="vmess2json convert vmess link to client json config.")
    parser.add_argument('-s',
                        action="store",
                        default="",
                        help="read from a subscribe url, display a menu to choose nodes")
    parser.add_argument('-p', help="this is the destined port number")
    option = parser.parse_args()
    if len(option.p) < 4:
        option.p = 19829
    if len(option.s):
        try:
            select_multiple(read_subscribe(option.s), option.p)
        except (EOFError, KeyboardInterrupt):
            print("Bye.")
        except BaseException:
            traceback.print_exc()
        finally:
            sys.exit(0)
