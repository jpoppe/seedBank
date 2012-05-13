#!/bin/sh
#
# seedBank daemon init script (c) 2009-2012 Jasper Poppe <jgpoppe@gmail.com>
#

### BEGIN INIT INFO
# Provides:          seedbank
# Required-Start:    $network $local_fs $named $remote_fs $syslog
# Required-Stop:     $network $local_fs $named $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: The seedBank daemon
# Description:       seedBank daemon is used by seedBank installations 
#                    for supplying the needed files, templates, 
#                    manifests, recipes, etc.. It is also used for 
#                    disabling hosts after as successful installation.
### END INIT INFO

NAME=seedbank
PIDFILE=/var/run/${NAME}.pid
DAEMON=/usr/bin/seedbank
DAEMON_OPTS="daemon --start"
PATH=/sbin:/bin:/usr/sbin:/usr/bin
START_SEEDBANK=false

if [ ! -f $DAEMON ]; then
	DAEMON=/usr/local/bin/seedbank
fi

[ -r /etc/default/$NAME ] && . /etc/default/$NAME

if [ $START_SEEDBANK != "true" ]; then
	echo "the seedBank daemon service is disabled, enable START_SEEDBANK in /etc/default/$NAME"
	exit 1
fi

check_process () {
	if [ -f $PIDFILE ]; then 
		if ps -p `cat $PIDFILE` > /dev/null; then
			echo "info: seedBank daemon is running"
			retval=2
		else
			echo "error: $PIDFILE found but seedBank daemon is not running"
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

		echo "starting seedBank daemon.."
		start-stop-daemon --background --start --make-pidfile --pidfile $PIDFILE --exec $DAEMON -- $DAEMON_OPTS
	;;

	stop)
		if [ -f $PIDFILE ]; then 
			echo "stopping seedBank daemon.."
			start-stop-daemon --stop --pidfile $PIDFILE
			rm $PIDFILE
		else
			echo "info: $PIDFILE not found, it the seedBank daemon is not running"
		fi
			
	;;

	status)
		if [ -f $PIDFILE ]; then 
			check_process
			if [ $retval = 3 ]; then
				echo "info: seedBank daemon is not running."
				exit 3
			fi
		else
			echo "info: seedBank daemon is not running."
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
