#!/bin/bash


IP={{inventory_hostname}}
TEST_FILE=/etc/sphinx_off
TIMEOUT=2

exit_code=0

if [ -f $TEST_FILE ]; then
	exit_code=98
else

    nc -w $TIMEOUT -z $IP 9306
    rez=$?
    if [[ $rez != 0 ]]; then
	    exit_code=99
    fi

    nc -w $TIMEOUT -z  $IP 3312
    rez2=$?
    if [[ $rez2 != 0 ]]; then
	    exit_code=99
    fi

fi


exit $exit_code








