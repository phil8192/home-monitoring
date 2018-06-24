#!/bin/bash
stdbuf -i0 -o0 -e0 pywws-testweatherstation -d -l 2>&1 \
  |python3 influx/influx_wh1080.py
