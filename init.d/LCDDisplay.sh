#!/bin/bash 
### BEGIN INIT INFO
#
# Provides: 		LCDDisplay
# Required-Start: 	$remote_fs
# Required-Stop: 	$remote_fs
# Default-Start: 	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description: 	Starts LCD Display interface
# Description: 		Starts LCD Display interface
#
### END INIT INFO

PROG="Adafruit_CharLCDPlate_IPclock_example.py"
PROG_PATH="/usr/local/bin/LCDDriver" ## Not need, but sometimes helpful (if $PROG resides in /opt for example).
PID_PATH="/var/run/"

start() {
    if [ -e "$PID_PATH/$PROG.pid" ]; then
        ## Program is running, exit with error.
        echo "Error! $PROG is currently running!" 1>&2
        exit 1
    else
        ## Change from /dev/null to something like /var/log/$PROG if you want to save output.
            $PROG_PATH/$PROG $PROG_ARGS 2>&1 >/dev/null &
        echo "$PROG started"
        touch "$PID_PATH/$PROG.pid"
    fi
}

stop() {
    if [ -e "$PID_PATH/$PROG.pid" ]; then
        ## Program is running, so stop it
        killall $PROG

        rm "$PID_PATH/$PROG.pid"
        
        echo "$PROG stopped"
    else
        ## Program is not running, exit with error.
        echo "Error! $PROG not started!" 1>&2
        exit 1
    fi
}

## Check to see if we are running as root first.
## Found at http://www.cyberciti.biz/tips/shell-root-user-check-script.html
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

case "$1" in
    start)
        start
        exit 0
    ;;
    stop)
        stop
        exit 0
    ;;
    reload|restart|force-reload)
        stop
        start
        exit 0
    ;;
    **)
        echo "Usage: $0 {start|stop|reload}" 1>&2
        exit 1
    ;;
esac
