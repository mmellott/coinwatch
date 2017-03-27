#!/bin/bash

pushover="$HOME/coinwatch/pushover.py"

notify=
msg=""

if !(pgrep flask &>/dev/null); then
    notify=:
    msg+="The flask server is NOT running"
fi

if !(pgrep watch.py &>/dev/null); then
    notify=:
    [[ -n $msg ]] && msg+=$'\n'
    msg+="The watch.py script is NOT running"
fi

if [[ $notify ]]; then
    "$pushover" "$msg"
fi
