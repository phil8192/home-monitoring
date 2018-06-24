#!/bin/bash
rtl_433 -F json |python3 influx/influx_n25fr.py
