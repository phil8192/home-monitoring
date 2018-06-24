import os
from influxdb import InfluxDBClient


def push_reading(db, reading):
    args = ['INFLUX_HOST', 'INFLUX_PORT', 'INFLUX_USER', 'INFLUX_PASS']
    conf = [os.environ.get(x) for x in args]
    conf.append(db)
    client = InfluxDBClient(*conf)
    try:
        client.write_points(reading)
    except Exception as ex:
        print(ex)
