# n25fr sensors -> influx
# reads n25ft status from stdin, push reading to influx.
# pushes on state change.
import os
import json
import time
import requests
from influx import push_reading


def weather_station_fun():
    last = {}
    def weather_station(reading):

        # hack: used station id as unique identifier in db, changes on frequency
        # change after reset. this should just be a conf parameter, not dynamic.
        stat = 'station_'+str(reading['id'])
        if stat == "station_166":
            stat = "station_188" # changed..

        rain = float(reading['rain']) # mm (cumulative? since when?)
        temp = float(reading['temperature_C'])
        humi = float(reading['humidity'])
        wind_gust = round(float(reading['gust']) * 0.621371, 2) # mph
        wind_speed = round(float(reading['speed']) * 0.621371, 2) # mph
       
        last_station_readings = last[stat] if stat in last else None

        tags = {
            'placement': 'out',
            'location': os.environ.get('LOCATION'),
            'sensor': 'n25fr',
            'id': stat
        }

        if last_station_readings is None:
            j = [
                { 'measurement': 'temp', 'tags': tags, 'fields': { 'value': temp } },
                { 'measurement': 'humidity', 'tags': tags, 'fields': { 'value': humi } },
                { 'measurement': 'rain', 'tags': tags, 'fields': { 'value': rain } },
                { 'measurement': 'wind_gust', 'tags': tags, 'fields': { 'value': wind_gust } },
                { 'measurement': 'wind_speed', 'tags': tags, 'fields': { 'value': wind_speed } }
            ]
            last[stat] = {'rain': rain, 'temp': temp, 'humi': humi, 'wind_gust': wind_gust, 'wind_speed': wind_speed}
        else:
            j = []
            if last[stat]['rain'] != rain:
                j.append({ 'measurement': 'rain', 'tags': tags, 'fields': { 'value': rain }})
                last[stat]['rain'] = rain
            if last[stat]['humi'] != humi:
                j.append({ 'measurement': 'humidity', 'tags': tags, 'fields': { 'value': humi }})
                last[stat]['humi'] = humi
            if last[stat]['temp'] != temp:
                j.append({ 'measurement': 'temp', 'tags': tags, 'fields': { 'value': temp }})
                last[stat]['temp'] = temp
            if last[stat]['wind_gust'] != wind_gust:
                j.append({ 'measurement': 'wind_gust', 'tags': tags, 'fields': { 'value': wind_gust }})
                last[stat]['wind_gust'] = wind_gust
            if last[stat]['wind_speed'] != wind_speed:
                j.append({ 'measurement': "wind_speed", 'tags': tags, 'fields': { 'value': wind_speed }})
                last[stat]['wind_speed'] = wind_speed
        
        # influx
        if len(j) > 0:
            push_reading('weather', j)
        else:
            print("dup")
       
        # also push garden data to wunderground.
        # note: should push this + others to local queue, then process concurrently.  
        if stat == 'station_188': # no other way to distinguish between sensors.....
            temp_f = round(temp*1.8+32, 2)
            payload = {
		'ID': os.environ.get('WUNDERGROUND_ID'),
                'PASSWORD': os.environ.get('WUNDERGROUND_PASS'),
                'dateutc': 'now',
                'tempf': temp_f,
                'windspeedmph': wind_speed,
                'windgustmph': wind_gust,
                'humidity': round(humi, 2),
                'softwaretype': 'pi',
                'realtime': 1,
                'rtfreq': 48
            }
            try:
                print("pushing to wunderground...")
                requests.get('https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php', params=payload)
            except:
                print("problem pushing to wunderground.")


    return weather_station


weather_station = weather_station_fun()


def process_reading(line):

    try:
        reading = json.loads(line)
    except:
        return

    print(json.dumps(reading, indent=2))    
    
    if 'model' in reading and reading['model'] == 'Fine Offset WH1050 weather station':
        weather_station(reading)

        

if __name__ == '__main__':
    import sys
    print("start")
    for line in sys.stdin:
        print("process {}".format(line))
        process_reading(line)
    print("bye.")
