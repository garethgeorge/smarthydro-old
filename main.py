import time
from threading import Thread
from datetime import datetime 
from w1thermsensor import W1ThermSensor
from lib.model import *
from lib.conversions import c_to_f
from flask import Flask, json, Response 

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdate

import itertools 
import io


tempSensors = W1ThermSensor()

airTempSensorMdl = declare_sensor("01193a5b6f21", "air temperature", "temp-c") # this is the probe marked with tape
nutrientTempSensorMdl = declare_sensor("01193a651085", "nutrient tank temperature", "temp-c")
commit()

def temp_samples_thread():
    sensors = list(W1ThermSensor.get_available_sensors())

    while True:
        for sensor in sensors:
            sensorMdl = get_sensor_by(sensor_hw_id=sensor.id)
            if not sensorMdl: 
                print("undeclared sensor: " + sensor.id + " detected, could not log its data")
                continue 
                
            try:
                record = Measurement(sensorMdl.sensor_id, int(time.time()), sensor.get_temperature())
            except Exception as e:
                print("Error reading temperature data: " + str(e))
                continue 
            
            print(record)
            insert_measurement(record)
        commit()
        
        time.sleep(60)

print("launching temperature sampler thread")
Thread(target=temp_samples_thread).start()

api = Flask(__name__)

@api.route('/get-data', methods=['GET'])
def get_data():
    return json.dumps([measurement._asdict() for measurement in query_measurements()]),200,{'content-type':'application/json'}

@api.route('/graphs/temperature', methods=['GET'])
def temperature_graph():
    # TODO: graphing code here 
    # https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask

    measurements = query_measurements(start_time=time.time() - 48 * 3600)
    measurements.sort(key=lambda x: (x.sensor_id, x.epoch_time))

    plt.style.use('dark_background')
    fig = Figure(figsize=(8, 6), dpi=200)
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_title(
        "Hydroponics Temperature Measurments (F)")
    legend = []

    for sensor_id, measurements in itertools.groupby(measurements, key=lambda x: x.sensor_id):
        measurements = list(measurements)
        ax1.plot(
            mdate.epoch2num([measurement.epoch_time for measurement in measurements]), 
            [c_to_f(measurement.value) for measurement in measurements]
        )
        legend.append(get_sensor_by(sensor_id).sensor_desc + " (current: %.1fF)" % c_to_f(measurements[-1].value))

    ax1.legend(legend)
    ax1.set_ylabel('Temperature (F)')
    ax1.set_xlabel('Timestamp')
    ax1.xaxis.set_major_formatter(mdate.DateFormatter('%d-%m-%y %H:%M:%S'))

    fig.autofmt_xdate()

    output = io.BytesIO()
    FigureCanvas(fig).print_jpeg(output)

    return Response(output.getvalue(), mimetype='image/jpeg')

api.run(host='0.0.0.0')
