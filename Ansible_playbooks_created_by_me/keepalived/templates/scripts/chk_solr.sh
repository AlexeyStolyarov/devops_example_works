#!/bin/bash


IP={{inventory_hostname}}
TEST_FILE=/etc/solr_off


if [ -f $TEST_FILE ]
    then
	exit 98
else
#    curl --connect-timeout 2  --fail http://$IP:8983/solr/admin/info/system?wt=json  > /dev/null 2>&1
    curl  --max-time 3  --fail http://$IP:8983/solr/admin/info/system?wt=json  > /dev/null 2>&1
    if [[ $? == "0" ]]
	then
	    exit 0
    else
        exit 99
    fi
fi






