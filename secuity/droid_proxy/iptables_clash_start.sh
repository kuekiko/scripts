#/bin/bash
if [ $# != 1 ] ; then
    echo "USAGE: $0 from to"
    echo " e.g.: $0 com.sankuai.meituan"
    exit 1;
fi
# $1 需要抓取的包名
NAME=$1
echo "packageName=$1"
# $2 本地透明代理的地址 127.0.0.1:16666
# TPROXY=$2
TPROXY="127.0.0.1:16666"
echo "transparent proxy address is $2"
# # $3 抓包代理的地址
# PROXY=$3
## 根据版本替换一下
clash="clash-linux-arm64"

## 运行root命令
runShellRoot(){
    CMD=$1
    result=`adb shell su -c "\"$1\""`
    if [ -n "$result" ]; then
        echo $result
    fi
}
## root下运行
## 保存原来的iptables规则 重启恢复
runShellRoot "iptables-save > /data/local/tmp/iptables.rules"

## 根据包名/进程名寻找uid
pslist=$(runShellRoot "ps -ef | grep $NAME | head -n 100 | cut -d ' ' -f 1")
# echo "$pslist"
# echo $pslist
## 排除掉 root shell system等无关uid
for i in $pslist;
do
    if [ $i != "root" -a "$i" != "shell" -a "$i" != "system" ]; then
        # echo $i
        UID=$i
    fi
done
echo "uid=$UID"
## UID为空
if [ ! -n "$UID" ]; then
    echo "UID is NULL, APP not running."
    exit 1;
fi
# UID=`runShellRoot "ps -ef | grep $NAME | head -n 1 | tail -n 1 |cut -d ' ' -f 1"`
## 检测redsocks2是否正在运行 ps -ef | grep redsocks2  运行则kill 有部分进程是假的 
rplist=$(runShellRoot "ps -ef | grep $clash | tr -s ' ' | cut -d ' ' -f 2")
if [ -n "$rplist" ]; then
    for i in $rplist;
    do
        # echo $i
        runShellRoot "kill -9 $i > /dev/null 2>&1"
    done
fi

## 安装运行redsocks2 arm64 默认
adb push $clash /data/local/tmp/
adb push config.yaml /data/local/tmp/
adb push Country.mmdb /data/local/tmp/
adb push set_iptables_clash.sh /data/local/tmp/
## todo 根据$PROXY 修改redsocks.conf
runShellRoot "chmod 777 /data/local/tmp/$clash"
runShellRoot "chmod 777 /data/local/tmp/set_iptables_clash.sh"
## iptable 转发到本地透明代理  需要去手动配置一下 http://yacd.haishan.me/ 填写手机的IP地址，规则选择proxy_socket5
## 默认流量全转发
runShellRoot "/data/local/tmp/set_iptables_clash.sh"
## 后台启动透明代理 先执行的话会阻塞
# runShellRoot "cd /data/local/tmp/ && nohup /data/local/tmp/$clash > /dev/null 2>&1 &"
## 阻塞 不后台
runShellRoot "cd /data/local/tmp/ && /data/local/tmp/$clash -d /data/local/tmp"

echo "DONE"