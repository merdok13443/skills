#!/bin/sh
# $1 = project dir
echo "window.TIMING=$(cat $1/timing.json);" > $1/timing.js
