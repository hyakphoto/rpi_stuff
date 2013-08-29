#!/usr/bin/python

import ptvsd
ptvsd.enable_attach(None)

from Adafruit_I2C          import Adafruit_I2C
from Adafruit_MCP230xx     import Adafruit_MCP230XX
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from subprocess            import * 
from time                  import sleep, strftime
from datetime              import datetime, timedelta
from Queue                 import Queue
from threading             import Thread

import smbus

# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
LCD = Adafruit_CharLCDPlate()

# Define a queue to communicate with worker thread
LCD_QUEUE = Queue()

# Button definitions
NONE           = 0x00
SELECT         = 0x01
RIGHT          = 0x02
DOWN           = 0x04
UP             = 0x08
LEFT           = 0x10
UP_AND_DOWN    = 0x0C
LEFT_AND_RIGHT = 0x12

BANNER = '  Raspberry Pi  \n     ready!     '

# ----------------------------
# WORKER THREAD
# ----------------------------

# Define a function to run in the worker thread
def update_lcd(q):
    while True:
        msg = q.get()
        # if we're falling behind, skip some LCD updates
        while not q.empty():
            q.task_done()
            msg = q.get()
        LCD.setCursor(0,0)
        LCD.message(msg)
        q.task_done()
    return

# Run some shell commands and fetch the output
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
    output = p.communicate()[0]
    return output

# Get the RPi's current IP
def get_ip():
    cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
    ipaddr = run_cmd(cmd).rstrip('\n')
    return ipaddr

# Get the RPi's uptime
def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    delta = timedelta(seconds = uptime_seconds)
    
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 60*60)
    minutes, seconds = divmod(remainder, 60)
   
    return '{}d {}:{}:{}'.format(delta.days, '%02d' % hours, '%02d' % minutes, '%02d' % seconds)

# Get the system date / time
def get_systime():
    return datetime.now().strftime('   %d.%m.%Y\n    %H:%M:%S\n')

# ----------------------------
# MAIN LOOP
# ----------------------------

def main():
    # Setup AdaFruit LCD Plate
    LCD.begin(16,2)
    LCD.clear()
    LCD.backlight(LCD.ON)
    
    # Create the worker thread and make it a daemon
    worker = Thread(target=update_lcd, args=(LCD_QUEUE,))
    worker.setDaemon(True)
    worker.start()
    
    # Display startup banner
    LCD_QUEUE.put(BANNER, True)
    
    #sleep(4)
    #LCD.clear()

    # Main loop
    while True:
        press = read_buttons()
               
        # SELECT button pressed
        if(press == SELECT):
           menu_pressed()
                
        delay_milliseconds(99)
    update_lcd.join()

# ----------------------------
# READ SWITCHES
# ----------------------------

def read_buttons():

   buttons = LCD.buttons()
   # Debounce push buttons
   if(buttons != 0):
      while(LCD.buttons() != 0):
         delay_milliseconds(1)
   return buttons



def delay_milliseconds(milliseconds):
   seconds = milliseconds / float(1000)	# divide milliseconds by 1000 for seconds
   sleep(seconds)

# ----------------------------
# MENU
# ----------------------------

def menu_pressed():
    MENU_LIST = [
        '1. Show System  \n   Information  ',
        '2. Show Clock   \n                ',
        '3. Shutdown     \n   System       ',
        '3. Exit         \n                ']
    
    item = 0
    LCD.clear()
    LCD_QUEUE.put(MENU_LIST[item], True)
    
    keep_looping = True
    while (keep_looping):
    
        # Wait for a key press
        press = read_buttons()
    
        # UP button
        if press == UP:
           item -= 1
           if item < 0:
              item = len(MENU_LIST) - 1
           LCD_QUEUE.put(MENU_LIST[item], True)
    
        # DOWN button
        elif press == DOWN:
           item += 1
           if item >= len(MENU_LIST):
              item = 0
           LCD_QUEUE.put(MENU_LIST[item], True)
    
        # SELECT button = exit
        elif press == SELECT:
           keep_looping = False
     
           # Take action
           if item == 0:
              # 1. show system information
              show_sysinfo()
           if item == 1:
              # 2. show clock
              show_clock()
           elif item == 2:
              # 3. shutdown the system
              shutdown_system()
        else:
           delay_milliseconds(99)
    
    # Restore display
    LCD_QUEUE.put(BANNER, True)

def shutdown_system():
    LCD_QUEUE.put('Shutting down\nSystem now! ... ', True)
    LCD_QUEUE.join()
    output = run_cmd("sudo shutdown now")
    LCD.clear()
    LCD.backlight(LCD.OFF)
    exit(0)

# -------------
# DISPLAY TIME 
# -------------

def show_clock():
   LCD.backlight(LCD.ON)
   i = 29
   
   keep_looping = True
   while (keep_looping):

      # Every 1/2 second, update the time display
      i += 1
      #if(i % 10 == 0):
      if(i % 5 == 0):
         LCD_QUEUE.put(get_systime(), True)

      # Every 100 milliseconds, read the switches
      press = read_buttons()

      # Take action on switch press   
      # SELECT button = exit
      if(press == SELECT):
         keep_looping = False
         
      delay_milliseconds(99)

# ----------------------------

# --------------------------
# DISPLAY SYSTEM INFORMATION
# --------------------------

def show_sysinfo():
    LCD.backlight(LCD.ON)
    i = 39
   
    keep_looping = True
    while (keep_looping):       
       i += 1
       # Every 4 seconds, update the time display
       if i == 120:
           i = 39
       if i == 80:
           # pad the string with space to have 16 characters (don't want to clear the display)
           uptime = '{0: <16}'.format(get_uptime())
           LCD_QUEUE.put('RPi Uptime:     \n' + uptime, True)           
       # ever
       if i == 40:
           ip = '{0: <16}'.format(get_ip())
           LCD_QUEUE.put('IP Address:     \n' + ip, True)

       # Every 100 milliseconds, read the switches
       press = read_buttons()

       # Take action on switch press   
       # SELECT button = exit
       if(press == SELECT):
           keep_looping = False
         
       delay_milliseconds(99)
# ----------------------------

if __name__ == '__main__':
  main()