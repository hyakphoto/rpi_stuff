import smbus
import time
import logging

class TempSensor:
    """

    Class to read out an DS1624 temperature sensor with a given address.

    Based on http://www.min.at/prinz/?x=entry:entry130204-184219
    
    DS1624 data sheet: http://datasheets.maximintegrated.com/en/ds/DS1624.pdf

    Thomas Heuberger, August 2013

    Usage:

        >>> from TempSensor import TempSensor
        >>> sensor = TempSensor(0x48)
        >>> print "%02.02f" % sensor.get_temperature()
        23.66

    """
    
    # Some constants
    DS1624_READ_TEMP = 0xAA
    DS1624_START = 0xEE
    DS1624_STOP = 0x22

    def __init__(self, address):
        self.address = address
        self.bus = smbus.SMBus(0)

    def __send_start(self):
        self.bus.write_byte(self.address, self.DS1624_START);

    def __send_stop(self):
        self.bus.write_byte(self.address, self.DS1624_STOP);

    def __read_sensor(self):         
        """    
        Gets the temperature data. As the DS1624 is Big-endian and the Pi Little-endian, 
        the byte order is reversed.
        
        """            

        """
        Get the two-byte temperature value. The second byte (endianness!) represents
        the integer part of the temperature and the first byte the fractional part in terms
        of a 0.03125 multiplier.
        The first byte contains the value of the 5 least significant bits. The remaining 3
        bits are set to zero.
        """
        return self.bus.read_word_data(self.address, self.DS1624_READ_TEMP)        

    def __convert_raw_to_decimal(self, raw):
        logging.basicConfig(filename='debug.log', level=logging.DEBUG)
        logging.debug('raw: ' + str(raw))
        logging.debug('raw bitstring: ' + bin(raw))

        # Remove the fractional part (first byte) by doing a bitwise AND with 0x00FF
        temp_integer = raw & 0x00FF
        logging.debug('integer: ' + str(temp_integer))
        logging.debug('integer bitstring: ' + bin(temp_integer))

        # Remove the integer part (second byte) by doing a bitwise AND with 0XFF00 and
        # shift the result bits to the right by 8 places and another 3 bits to the right 
        # because LSB is the 5th bit          
        temp_fractional = ((raw & 0xFF00) >> 8) >> 3
        logging.debug('fractional: ' + str(temp_fractional))
        logging.debug('fractional bitstring (>>8>>3): ' + bin(temp_fractional))
        
        # If the temperature is negative (second byte has a leading 1) ...
        if (temp_integer & 0x80) == 0x80:            
            temp_fractional = (~temp_fractional) + 1
            logging.debug('negative!: ' + str(temp_fractional))
        return temp_integer + ( 0.03125 * temp_fractional)
    
    def run_test(self):
        # Examples taken from the data sheet
        values = [0x7D, 0x1019, 0x8000, 0, 0x80FF, 0xF0E6, 0xC9]

        for value in values:
            logging.debug('value: ' + hex(value) + ' result: ' + str(self.__convert_raw_to_decimal(value)))

    def get_temperature(self):
        self.__send_start();
        time.sleep(0.1);
        return self.__convert_raw_to_decimal(self.__read_sensor())