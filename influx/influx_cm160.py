import os
import json
import time
from influx import push_reading


def process_reading(watts):
    j = {
        'tags': 
        {
            'location': os.environ.get('LOCATION')
        },
        'measurement': 'watts',
        'fields': 
        { 
            'value': watts 
        } 
    }
    push_reading('power', [j]) 


if __name__ == '__main__':
    import sys
    print("start")
    last = -1
    for line in sys.stdin:
        print(line)
        #LIVE: 22/10/2016 15:46 : 2016.000000 W  
        if not line.startswith("LIVE"):
            continue
        l = line.split()
        w = int(float(l[4]))
        if w == last:
            continue
        process_reading(w)
        last = w

    print("bye.")
