#!/bin/sh
#
# seedbank daemon init script (c) 2009-2011 Jasper Poppe <jpoppe@ebay.com>
#

### BEGIN INIT INFO
# Provides:          seedbank
# Required-Start:    $network $local_fs $named $remote_fs $syslog
# Required-Stop:     $network $local_fs $named $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: The seedbank daemon
# Description:       seedbank daemon is used by seedbank installations 
#                    for supplying the needed files, templates, 
#                    manifests, recipes, etc.. It is also used for 
#                    disabling hosts after as successful installation.
### END INIT INFO

NAME=seedbank_daemon
PIDFILE=/var/run/${NAME}.pid
DAEMON=/usr/bin/seedbank_daemon
DAEMON_OPTS="-d"
PATH=/sbin:/bin:/usr/sbin:/usr/bin

check_process () {
	if [ -f $PIDFILE ]; then 
		if ps -p `cat $PIDFILE` > /dev/null; then
			echo "info: seedbank daemon is running"
			retval=2
		else
			echo "error: $PIDFILE found but seedbank daemon is not running"
			rm $PIDFILE
			echo "info: $PIDFILE removed"
			retval=3
		fi
	else
		retval=1
	fi		
}

case ${1} in
	start)
		check_process

		if [ $retval = 2 ]; then
			exit 0
		fi

		echo "starting seedbank daemon.."
		start-stop-daemon --background --start --make-pidfile --pidfile $PIDFILE --exec $DAEMON -- $DAEMON_OPTS
	;;

	stop)
		if [ -f $PIDFILE ]; then 
			echo "stopping seedbank daemon.."
			start-stop-daemon --stop --pidfile $PIDFILE
			rm $PIDFILE
		else
			echo "info: $PIDFILE not found, it the seedbank daemon is not running"
		fi
			
	;;

	status)
		if [ -f $PIDFILE ]; then 
			check_process
			if [ $retval = 3 ]; then
				echo "info: seedbank daemon is not running."
				exit 3
			fi
		else
			echo "info: seedbank daemon is not running."
			exit 3
		fi
			
	;;

	restart)
		${0} stop
		${0} start
	;;

	*)
		echo "Usage: ${0} {start|stop|restart|status}"
	;;

esac
