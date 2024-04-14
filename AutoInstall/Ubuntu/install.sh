#/bin/sh
## Linux 启动
TMP_PATH = "~/TMP"
SECTOOLS_PATH = "~/sectools"
SOURCE = ""
PIP3_SOURCE = ""
## A
mkdir $TMP_PATH
mkdir $SECTOOLS_PATH
## 1.切换源

sudo apt update && sudo apt upgrade
## 2.安装基本依赖和工具
sudo apt install wget git curl
sudo apt install python3-pip
sudo apt install texinfo help2man libtool libtool-bin libncurses5 libncurses-dev libncursesw5-dev libpixman-1-dev libglib2.0-dev pkg-config
### 基础工具链
sudo apt install gcc gdb gcc-multilib gdb-multiarch
### i386环境
sudo apt install linux-libc-dev linux-libc-dev:i386
### jdk 17 ++
sudo apt install openjdk-17-jdk

## 3.编译/下载安装、升级一些工具
### clang\llvm 工具链

### Android SDK 工具链

### CMAKE 高版本

source ~/env.sh
### ninja
git clone https://github.com/ninja-build/ninja
cd ninja
 ## ./configure.py --bootstrap ## 有python2
 ## 使用cmake
cmake -Bbuild-cmake -H.
cmake --build build-cmake
cp ./build-cmake/ninja /usr/bin/
source ~/env.sh
### autoconf 有的软件需求
echo "Install autoconf-2.71" 
curl -O http://mirrors.kernel.org/gnu/autoconf/autoconf-2.71.tar.gz
tar -xzvf autoconf-2.71.tar.gz
cd autoconf-2.71
./configure --prefix=/usr/local
make
sudo make install

### qemu高版本

### 安全工具
#### redare2 cutter 一类

#### binwalk

#### codeQL

#### gdb调试

### golang

### Rust

### 可选的交叉编译工具


### python3 一些库
#### 修改pip3 源

#### ipython frida 
pip3 install ipython frida
