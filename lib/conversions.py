import math 

def c_to_f(c):
    return c * 1.8 + 32.0

def calc_resistance(rKnown, maxV, measuredV):
    measuredV = min(maxV, measuredV)
    if abs(measuredV - maxV) < 0.01:
        return math.inf

    return measuredV / (maxV - measuredV) * rKnown


# 5000 ohms the water (ground)
# 4700 ohms the resistor (positive)
# 3.3 V in so we would expect 1.5 across the two