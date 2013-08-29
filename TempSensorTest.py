from TempSensor import TempSensor
import logging

def main():
    # disable logging

    # logging.disable(logging.CRITICAL)

    sensor = TempSensor(0x48)
    print "%02.02f" % sensor.get_temperature()

if __name__ == "__main__":
    main()