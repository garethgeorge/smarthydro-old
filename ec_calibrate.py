from w1thermsensor import W1ThermSensor
from lib.conversions import c_to_f, calc_resistance

import board
import busio
import time 
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# user parameters
calibrate_ec = 1765 # or something 

# temperature coefficients
temp_coeff = 0.019
sensor = W1ThermSensor(sensor_id="01193a651085")
temp_c = sensor.get_temperature()

calibrate_ec_adjusted = calibrate_ec * (1+(temp_coeff*(temp_c-25.0)))

# setup pins
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

chan = AnalogIn(ads, ADS.P0)
while True:
    # https://www.raspberrypi.org/forums/viewtopic.php?t=164147

    temp_c = sensor.get_temperature()
    resistance = calc_resistance(4.6 * 1000, 3.0, chan.voltage)
    print("resistance: " + str(resistance))
    K = calibrate_ec * resistance 
    print("K: " + str(K))

    # K = 1000.0/(rc*calibrate_ec_adjusted)
    # print("K: " + str(K))
    # EC = 1000.0/(rc*K)
    # EC25  =  EC / (1.0 + temp_coeff * (temp_c-25.0))
    # print("EC: " + str(EC) + " EC25: " + str(EC25))

    time.sleep(1)