#!/bin/bash

PID_FILE=~/kanjitrainer.pid

if [[ -f $PID_FILE ]]; then
    kill $(cat $PID_FILE)
fi

python3 kanjitrainer.py &
echo $! > ~/kanjitrainer.pid
