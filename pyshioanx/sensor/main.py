# main.py

from heartrate_monitor import HeartRateMonitor
import time
import argparse

parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-r", "--raw", action="store_true",
                    help="print raw data instead of calculation result")
parser.add_argument("-t", "--time", type=int, default=60,
                    help="duration in seconds to read from sensor, default 30")
# DIUBAH: Tambahkan argumen untuk loop time
parser.add_argument("-l", "--loop", type=float, default=1.0,
                    help="loop time in seconds for the sensor thread, default 1.0")
args = parser.parse_args()

print('sensor starting...')
# DIUBAH: Teruskan argumen loop_time ke constructor
hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw), loop_time=args.loop)
hrm.start_sensor()
try:
    time.sleep(args.time)
except KeyboardInterrupt:
    print('keyboard interrupt detected, exiting...')

hrm.stop_sensor()
print('sensor stoped!')