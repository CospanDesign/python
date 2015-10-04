#! /usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import math

CONTROLLER_PERIOD = 5.0 * 10**-6
STEP_LENGTH = 250 * 10 ** -9
TOTAL_STEPS_PER_CONTROL_PERIOD = int((CONTROLLER_PERIOD / STEP_LENGTH) + 1.0)




if __name__ == "__main__":
    print "Controller Period Length: %f (uS)" % (CONTROLLER_PERIOD / 10 ** -6)
    print "Step Length: %f(uS)" % (STEP_LENGTH / 10 ** -6)
    print "Total Steps Per Count: %f(uS)" % TOTAL_STEPS_PER_CONTROL_PERIOD
