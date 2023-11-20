# 使用说明

## 抓包相关配置

### redsocks2

配置redsock2.conf文件

```json
base {
    log_debug = off;
    log_info = on;
    log = stderr;
    daemon = off;
    redirector = iptables;
}

redsocks {
    bind = "127.0.0.1:16666"; // 本地监听透明代理地址
    relay = "10.19.196.26:8889"; //远程代理地址 charles bp 等
    type = socks5;
    autoproxy = 0;
    timeout = 13;
}
```

自动化自动透明代理抓包
使用Linux系统 设备已经通过USB或者网络连接 设备具有root权限

在当前目录执行
`sh iptables_redsock2_start.sh [PackageName] [Tproxy]`

### clash

配置文件config.yaml

```yaml
# TProxy 的透明代理端口
tproxy-port: 7893

# mixed-port 端口将同时支持 SOCKS5/HTTP
mixed-port: 7890

# RESTful API for clash
external-controller: 0.0.0.0:9090

allow-lan: true

mode: global

log-level: debug

bind-address: 0.0.0.0

dns:
    enable: true
    listen: 0.0.0.0:1053
    ipv6: true
    enhanced-mode: fake-ip
    nameserver:
      - 114.114.114.114

proxies:
  - name: "proxy_socks5"
    # 记住抓包软件的代理类型应该是 socks5
    type: socks5
    # 请修改为自己抓包软件的 ip 和 端口
    server: 10.19.196.26
    port: 8889
    udp: true

  - name: "proxy_http"
    type: http
    server: 10.19.196.26
    port: 8888
    udp: true
    
proxy-groups:

rules:
```