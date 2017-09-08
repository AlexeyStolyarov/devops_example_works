#!/bin/bash

## file placed into /usr/share/jq2ch
##
## todo!! make file storage in RAM disk
##
##

DIR_BASE=/mnt/volumes/IPFIX2ClickHouse
DIR_WRK=$DIR_BASE
DIR_TMP=$DIR_BASE/tmp
FILE_LOG=$DIR_BASE/logfile
PYTHON_EXEC=/usr/share/jq2ch/json2ch.py

if [ ! -d $DIR_TMP ]
then
    mkdir $DIR_TMP
fi

touch $FILE_LOG
if [ `stat --printf="%s\n"  $FILE_LOG` -gt 10240 ]
then
    truncate -s 0 $FILE_LOG
fi


#  JSON_data
#   mktemp --tmpdir=$DIR_TMP
#  "dot1qCustomerVlanId": 0
#  "dot1qVlanId": 0
#  "flowEndReason": 2
#  "flowEndMilliseconds": "2017-08-31T08:49:36.149"
#  "flowStartMilliseconds": "2017-08-31T08:48:58.042"
#  "maximumTTL": 54
#  "minimumTTL": 54
#  "packetDeltaCount": 2
#  "octetDeltaCount": 140
#  "egressInterface": 603
#  "icmpTypeCodeIPv4": 0
#  "destinationTransportPort": 53
#  "sourceTransportPort": 6606
#  "protocolIdentifier": "UDP"
#  "ipClassOfService": 0
#  "destinationIPv4Address": "195.226.222.19"
#  "sourceIPv4Address": "213.150.78.106"
#  "@type": "entry"
#  "ingressInterface": 606
#  "vlanId": 0
#  "sourceIPv4PrefixLength": 19
#  "destinationIPv4PrefixLength": 24
#  "bgpSourceAsNumber": 13095
#  "bgpDestinationAsNumber": 197200
#  "ipNextHopIPv4Address": "0.0.0.0"
#  "tcpControlBits": "......"                              

# CREATE TABLE default.nflow
# (
# date Date,                      --  flowStartMilliseconds
# dateTime DateTime,              -- flowStartMilliseconds
# duration UInt64,                -- (flowEndMilliseconds - flowStartMilliseconds)
# packetDeltaCount        UInt64,
# octetDeltaCount         UInt64, 
# egressInterface         String,
# destinationTransportPort UInt32,
# sourceTransportPort      UInt32,
# protocolIdentifier       String,  
# destinationIPv4Address   String,
# sourceIPv4Address        String,
# ingressInterface         String,
# sourceIPv4PrefixLength   String,
# destinationIPv4PrefixLength  String,
# bgpSourceAsNumber            UInt32,
# bgpDestinationAsNumber       UInt32,
# direction               String
# )
# ENGINE = MergeTree(date, (dateTime),8192);

PREFIX="default.nflow"
TABLE_TODAY="${PREFIX}_full"


for i in `find $DIR_WRK -type f -name 'json.*' -mmin +1`;
#for i in `find . -type f -name 'json.201708311035' -mmin +1`;
do
     date >> $FILE_LOG
     echo "processing $i" >> $FILE_LOG
     echo "---------------------" >> $FILE_LOG
     tmp=$(mktemp  --tmpdir=$DIR_TMP)

    $PYTHON_EXEC $i > $tmp

    cat $tmp | clickhouse-client --port 9008 --query="INSERT INTO $TABLE_TODAY  FORMAT CSV"
    rm $tmp

#    clear old file
    rm $i
#
done

