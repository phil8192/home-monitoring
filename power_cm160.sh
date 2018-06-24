#!/bin/bash
stdbuf -i0 -o0 -e0 cm160 |python3 influx/influx_cm160.py

