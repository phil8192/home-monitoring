# weather base station -> influx
# reads base station status from stdin, push reading to influx.
# status obtained from pywws-testweatherstation -d -l.
# pushes on state change.
import os
import json
from influx import push_reading


def weather_station_fun():
    last = {'pressure': None, 'temp': None, 'humidity': None}
    def weather_station(reading):
        temp = float(reading['temp_in'])
        humi = float(reading['hum_in'])
        pres = float(reading['abs_pressure'])
       
        tags = {
            'placement': 'in',
            'location': os.environ.get('LOCATION'),
            'sensor': 'w8681',
            'id': 'w8681'
        }

        j = []
        if last['pressure'] != pres:
            j.append({
                'measurement': 'pressure',
                'tags': tags,
                'fields': {
                    'value': pres
                }
            })
            last['pressure'] = pres
        if last['humidity'] != humi:
            j.append({
                'measurement': 'humidity',
                'tags': tags,
                'fields': {
                    'value': humi
                }
            })
            last['humi'] = humi
        if last['temp'] != temp:
            j.append({
                'measurement': 'temp',
                'tags': tags,
                'fields': {
                    'value': temp
                }
            })
            last['temp'] = temp
        
        # push to influx
        if len(j) > 0:
            push_reading('weather', j)
        else:
            print("dup")


    return weather_station


weather_station = weather_station_fun()


def process_reading(line):
    print(line)
    reading = eval(line) 
    print(json.dumps(reading, indent=2))    
    weather_station(reading)


if __name__ == '__main__':
    import sys
    import re
    print("start")
    for line in sys.stdin:
        print("process {}".format(line))
        if "{'status':" in line:
            raw = re.sub("^.*{", "{", line)
            process_reading(raw)
    print("bye.")
