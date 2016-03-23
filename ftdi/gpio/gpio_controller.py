
import os
import sys
import time
from array import array as Array
from pyftdi.ftdi import Ftdi

class GPIOController(object):

    def __init__(self, vendor, product, interface = 0):
        self.f = Ftdi()
        self.vendor = vendor
        self.product = product
        self.interface = interface
        self.f.open_bitbang(self.vendor, self.product, self.interface)

    def read_pins(self):
        """
        Read all pins

        Args:
            Nothing

        Returns (int):
            All pins
        """
        return self.f.read_pins()

    def read_pin(self, bit_index):
        """
        Reads the pin specified by bit index:

        Args:
            bit_index (int): 0 - 15

        Returns (Boolean)
            True if set
            False if not set
        """
        bit_mask = 1 << bit_index
        return (self.f.read_pins() & bit_mask > 0)

    def enable_pin(self, bit_index, enable):
        """
        write out a single pin

        Args:
            bit_index (int):
                Index of bit to set
            enable (Boolean):
                True: Set
                False: Clear

        Returns: Nothing
        """
        bit_mask  = 1 << bit_index
        pins = self.f.read_pins()
        if enable:
            pins |= bit_mask
        else:
            pins &= ~bit_mask

        self.enable_pins(pins, enable)

    def enable_pins(self, bit_mask, enable):
        """
        write out multiple pins at one time 

        Args:
            bit_mask: The set of pins to be set or not set
                a 0 in a bit setting would set the pin low
                a 1 in a bit setting would set the pin high

        Returns: Nothing

        Example:
            enable_pins(bit_mask = 0x11)
            would set pins at address 0 and at address 4 high
            while the rest would be low
        """
        bit_mask = 0xFF & bit_mask
        if enable:
            self.f.write_data(Array('B', [0x01, bit_mask]))
        else:
            self.f.write_data(Array('B', [0x00, bit_mask]))

    def set_pin_direction_mask(self, pins):
        """
        Configure the GPIO direction

        Args:
            pins (integer): bitmask of pin direction
                1 = output, 0 = input

        Returns: Nothing

        Example:
            Set bit 0 and bit 4
            set_pin_direction_mask(0x11)

        Returns:
        """
        self.f.open_bitbang(self.vendor,
                            self.product,
                            self.interface,
                            direction = pins)
