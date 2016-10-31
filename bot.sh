#!/bin/bash
cd "$(dirname "$0")"

INIT_CMD="python3 main.py"
PID_FILE="bot.pid"

TRANSLATE_LIB_URL="git@bitbucket.org:illemius/translatelib.git"

case $1 in
    setup)
        git clone ${TRANSLATE_LIB_URL} TranslateLib
        cp config.example.py config.py
        nano config.py
    ;;
    start)
        ${INIT_CMD}
    ;;
    background|bg)
        if  [ -f "$PID_FILE" ]; then
            PID=`cat ${PID_FILE}`
            if ps -p ${PID} > /dev/null; then
                echo "Bot already started! " >&2
                exit
            fi
        fi
        echo "Run in background"
        ${INIT_CMD} &
        MyPID=$!
        echo "-> [$MyPID]"
        echo ${MyPID} > ${PID_FILE}
        exit
    ;;
    stop)
        if ! [ -f "$PID_FILE" ]; then
            echo "PID file not found."
        else
            PID=`cat ${PID_FILE}`
            if ! kill ${PID} > /dev/null 9>&1; then
                echo "Could not send SIGTERM to process $PID" >&2
            else
                echo "Killed."
                rm bot.pid
            fi
        fi
    ;;
    *)
        echo "Usage: '$0 start|background|stop'"
    ;;
esac
