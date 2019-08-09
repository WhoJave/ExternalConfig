# ExternalConfig

#### 使用说明

- 项目中使用的python3路径为 `/usr/local/bin/python3`，请自行安装
- 生成配置的路径为`~/Documents/Surge/config`
- 请将ss-local文件复制到`~/Documents/Surge/config`目录下
- `~/Documents/Surge/config/external.txt`External配置文件
- 关于`ss-local（此处指的是SSR）`ShadowsocksX-NG-R8安装后在`~/Library/Application Support/ShadowsocksX-NG/ss-local-2.5.6.9.static`这个路径下可找到
- 参考:https://community.nssurge.com/d/3-external-proxy-provider 启动后可在`/tmp`路径看到log
- `v2ray`同理

#### TODO

- [ ] v2ray订阅转换External

配置参考:

>- 示例：
>
>```json
>SSR东京2上海 = external, exec = "/Users/你的用户名/Documents/Surge/config/ss-local", local-port = 1091, args = "-c", args = "/Users/你的用户名/Documents/Surge/config/SSR东京2上海.json"
>香港5v2ray = external, exec = "/Users/你的用户名/Documents/Surge/config/v2ray", local-port = 1098, args = "--config=/Users/你的用户名/Documents/Surge/config/香港5v2ray.json"
>```
>
>注意：上文配置中 `local-port`要与下文json配置中的`local-port`保持一致
>
>- SSR东京2上海.json
>
>```json
>{
>  "local_address" : "127.0.0.1",
>  "local_port" : 1091,
>  "server" : "服务器地址",
>  "server_port" : 8888,
>  "method" : "aes-256-cfb",
>  "protocol" : "auth_chain_a",
>  "protocol_param" : "",
>  "timeout" : 60,
>  "obfs" : "tls1.2_ticket_auth",
>  "obfs_param" : "cloudflare.com",
>  "password" : "你的密码"
>}
>```
>
>- 香港5v2ray.json
>
>```json
>{
>    "log": {
>        "loglevel": "info"
>    },
>    "inbound": {
>        "listen": "127.0.0.1",
>        "port": 1098,
>        "protocol": "socks",
>        "settings": {
>            "auth": "noauth",
>            "udp": true,
>            "ip": "127.0.0.1"
>        }
>    },
>    "outbound": {
>        "protocol": "vmess",
>        "settings": {
>            "vnext": [
>                {
>                    "address": "你的服务器",
>                    "port": 8888,
>                    "users": [
>                        {
>                            "id": "你的id",
>                            "alterId": 2
>                        }
>                    ]
>                }
>            ]
>        }
>    }
>}
>
>```
>
>注：`v2ray`inboud中配置的port需要与配置文件中的`local-port`一致