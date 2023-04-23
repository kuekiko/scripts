#!/bin/bash
ARM64="./bin/share_arm64_android"
ARM="./bin/share_arm_android"
I386="./bin/share_386_android"
AMD64="./bin/share_amd64_android"
GO="/usr/local/go/bin/go"


export CGO_ENABLED=1
echo "build $ARM64"
export GOOS=android
export CC=${NDK_ROOT}/24.0.8215888/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android30-clang 
export GOARCH=arm64 
$GO build -o $ARM64 main.go
# md5sum $ARM64 | cut -d " " -f1 > $ARM64.md5
# go build -o $ARM64 main.go

echo "build $ARM"
export CC=${NDK_ROOT}/24.0.8215888/toolchains/llvm/prebuilt/linux-x86_64/bin/armv7a-linux-androideabi31-clang
export GOARCH=arm
$GO build -o $ARM main.go
# md5sum $ARM | cut -d " " -f1 > $ARM.md5
# go build -o $ARM main.go

# export CC=${NDK_ROOT}/24.0.8215888/toolchains/llvm/prebuilt/linux-x86_64/bin/i686-linux-android30-clang
# export GOARCH=386
# $GO build -o $I386 main.go
# md5sum $I386 | cut -d " " -f1 > $I386.md5
# go build -o ./bin/Android_agent_386 main.go

echo "build $AMD64"
export CC=${NDK_ROOT}/24.0.8215888/toolchains/llvm/prebuilt/linux-x86_64/bin/x86_64-linux-android30-clang
export GOARCH=amd64
$GO build -o $AMD64 main.go
# md5sum $AMD64 | cut -d " " -f1 > $AMD64.md5
# go build -o $AMD64 main.go
## 静态 Linux
export CGO_ENABLED=0
export GOOS=linux
ARM64="./bin/share_arm64_linux_static"
ARM="./bin/share_arm_linux_static"
I386="./bin/share_386_linux_static"
AMD64="./bin/share_amd64_linux_static"

echo "build $ARM64"
export GOARCH=arm64 
$GO build -o $ARM64 main.go

echo "build $ARM"
export GOARCH=arm
$GO build -o $ARM main.go

echo "build $AMD64"
export GOARCH=amd64
$GO build -o $AMD64 main.go

## Windows

## MIPS
MIPS="./bin/share_mips_linux"
MIPSLE="./bin/share_mipsle_linux"
export GOOS=linux
echo "build $MIPS"
export GOARCH=mips
$GO build -o $MIPS main.go

echo "build $MIPSLE"
export GOARCH=mipsle
$GO build -o $MIPSLE main.go

## MIPS64
