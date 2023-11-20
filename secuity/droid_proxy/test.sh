NAME="com.hikvision.moa"

RUN_SHELL_ROOT $NAME

RUN_SHELL_ROOT(){
    CMD=$1
    ehco "exec root command $1"
    adb shell su -c "\"$1\""
}