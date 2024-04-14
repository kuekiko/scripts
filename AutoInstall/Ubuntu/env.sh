## 存储自定义的一些的环境变量 防止部分环境污染
## 使用方法
### 在 ~/.bashrc or /etc/bash.bashrc or ~/.zshrc or /etc/zsh/zshrc 等shell的文件末尾加入上source ~/env.sh (path自定义)

## 自用环境 WSL
## Android SDK
export ANDROID_SDK_ROOT=/mnt/d/WSL_Tools/Android_SDK
export PATH=$PATH:${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin
export PATH=$PATH:${ANDROID_SDK_ROOT}/platform-tools
export PATH=$PATH:${ANDROID_SDK_ROOT}/tools
export NDK_ROOT=/mnt/d/WSL_Tools/Android_SDK/ndk
export PATH=$PATH:${NDK_ROOT}/24.0.8215888

## golang
export PATH=$PATH:/usr/local/go/bin

## rust
source "$HOME/.cargo/env"

## tools WSL as root
alias binwalk="binwalk --run-as=root"

## rust
source "$HOME/.cargo/env"

## wsl2 proxy 新版本会自动套用Win的环境 无需设置
host_ip="127.0.0.1"
alias setproxy="export all_proxy=http://$host_ip:10809;export http_proxy=http://$host_ip:10809;export https_proxy=http://$host_ip:10809;"
alias unsetproxy="unset all_proxy;unset http_proxy;unset https_proxy;"

## go 国内源

## build root

## ulibc 交叉编译链 同上