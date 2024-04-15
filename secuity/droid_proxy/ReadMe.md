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

## Windows powerShell脚本使用说明

需要先解除执行脚本限制，需要先以管理员权限执行：`Set-ExecutionPolicy AllSigned` 之后需要签名，比较麻烦。。
执行 `Get-ExecutionPolicy`检查当前的状态

```powershell
PS C:\Windows\system32> Set-ExecutionPolicy AllSigned

执行策略更改
执行策略可帮助你防止执行不信任的脚本。更改执行策略可能会产生安全风险，如 https:/go.microsoft.com/fwlink/?LinkID=135170
中的 about_Execution_Policies 帮助主题所述。是否要更改执行策略?
[Y] 是(Y)  [A] 全是(A)  [N] 否(N)  [L] 全否(L)  [S] 暂停(S)  [?] 帮助 (默认值为“N”): y
```

简单的本地签名命令：
```powershell
$cert = New-SelfSignedCertificate -DnsName "yourdomain.com" -CertStoreLocation "Cert:\CurrentUser\My" -Type CodeSigningCert
Set-AuthenticodeSignature -FilePath "path\to\your\script.ps1" -Certificate $cert
```

！！ 危险操作：`Set-ExecutionPolicy RemoteSigned`  这样可以在本地运行未签名的ps1脚本。