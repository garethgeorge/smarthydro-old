# pip3 install adafruit-circuitpython-ads1x15
# https://hackaday.io/project/7008-fly-wars-a-hackers-solution-to-world-hunger/log/24646-three-dollar-ec-ppm-meter-arduino
import math 
import board
import busio
import time 
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from lib.conversions import c_to_f, calc_resistance
from w1thermsensor import W1ThermSensor

# pure water PPM is 20
# tank is 645 at 73.4 farenheight
# tank ppm is at 860


# constants, this is the one recommended for most plant nutrient solutions 
# temp_coeff = 0.019
K = 3055229.042239706
sensor = W1ThermSensor(sensor_id="01193a651085")

# setup pins
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

chan = AnalogIn(ads, ADS.P0)
while True:
    # https://www.raspberrypi.org/forums/viewtopic.php?t=164147

    temp_c = sensor.get_temperature()
    resistance = calc_resistance(4.7 * 1000, 3.3, chan.voltage)

    ec = 1/resistance*K

    print("\nvoltage: " + str(chan.voltage) + " rc: " + str(resistance) + " ec: " + str(ec))

    # EC = 1000.0/(rc*K)
    # EC25  =  EC / (1.0 + temp_coeff * (temp_c-25.0))
    # print("voltage: %.2f resistance: %.2f ec: %.2f" % (chan.voltage, rc, EC25))
