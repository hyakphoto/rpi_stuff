from TempSensor import TempSensor
import logging

def main():
    # disable logging

    # logging.disable(logging.CRITICAL)

    sensor = TempSensor(0x48)
    sensor.get_temperature()

if __name__ == "__main__":
    main()