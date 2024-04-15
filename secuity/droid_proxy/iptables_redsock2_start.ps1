# 检查参数数量
if ($args.Count -ne 1) {
    Write-Host "USAGE: $0 app_package_name"
    Write-Host " e.g.: $0 com.sankuai.meituan"
    exit 1
}

$Name = $args[0]
Write-Host "packageName=$Name"

$TProxy = "127.0.0.1:16666"
Write-Host "transparent proxy address is $TProxy"

$Redsocks = "redsocks2_arm64"

# 函数：在Android设备上执行需要root权限的命令
function RunShellRoot {
    param ([string]$command)
    Write-Host "Executing command: adb shell su -c `"$command`""
    $result = adb shell su -c "`"$command`""
    if ($result) {
        Write-Output $result
    } else {
        Write-Host "No output or error received"
    }
}

# 保存现有的iptables规则
$iptablesBackup = RunShellRoot "iptables-save > /data/local/tmp/iptables.rules"
if ($iptablesBackup -match "Permission denied") {
    Write-Host "Failed to save iptables rules, permission denied"
    exit 1
}

# 获取应用的用户ID
$pslist = RunShellRoot "ps -ef | grep $Name | head -n 100 | cut -d ' ' -f 1"
$UserID = $null
foreach ($line in $pslist -split "`n") {
    if ($line -notmatch "root|shell|system") {
        $UserID = $line.Trim()
        break
    }
}

if (-not $UserID) {
    Write-Host "USERID is NULL, APP not running."
    exit 1
}
Write-Host "uid=$UserID"

# 检测并终止任何正在运行的redsocks进程
$rplist = RunShellRoot "ps -ef | grep $Redsocks | tr -s ' ' | cut -d ' ' -f 2"
foreach ($processID in $rplist -split "`n") {
    if ($processID) {
        RunShellRoot "kill -9 $processID"
    }
}

# 上传redsocks二进制文件和配置文件
adb push $Redsocks /data/local/tmp/
adb push redsocks.conf /data/local/tmp/
RunShellRoot "chmod 777 /data/local/tmp/$Redsocks"

# 配置iptables，将指定app的流量转发到透明代理
$iptablesCommand = "iptables -t nat -A OUTPUT -p tcp ! -d 127.0.0.1 -m owner --uid-owner $UserID --dport 0:65535 -j DNAT --to-destination $TProxy"
RunShellRoot $iptablesCommand

# 运行redsocks并指定配置文件
$redsocksStartCommand = "cd /data/local/tmp/ && /data/local/tmp/$Redsocks -c /data/local/tmp/redsocks.conf"
RunShellRoot $redsocksStartCommand

Write-Host "DONE"
