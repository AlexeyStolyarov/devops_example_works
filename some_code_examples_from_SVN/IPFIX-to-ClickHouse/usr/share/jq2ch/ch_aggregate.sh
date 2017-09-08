#!/bin/bash

#  1. this script should be runned at beginnning of each hour
#  2. it takes date from previous hour and inserts it into aggregated table
#  SQL=	select   date,  toStartOfHour(dateTime) t,  sum(packetDeltaCount), sum(octetDeltaCount), direction, operator, protocolIdentifier
#	from default.nflow  where date = today() and dateTime = toStartOfHour(now() )-1
#	group by  date, t,  direction, operator, protocolIdentifier
#	order by t, operator, direction
#  3. if time > 23:00 - create if not exist table for next_day
#  4. if time > 01:00 - drop table from previous day
#  5. json2ch should write data into current_day table.



PREFIX="default.nflow"

#DAY_TODAY=`date +"%Y_%m_%d"`
#DAY_YESDY=`date --date="-1 day" +"%Y_%m_%d"`
#DAY_TMROW=`date --date="+1 day" +"%Y_%m_%d"`



TABLE_AGGREGATED="${PREFIX}_aggreg"
TABLE_FULL="${PREFIX}_full"
#TABLE_TODAY="${PREFIX}_${DAY_TODAY}"
#TABLE_TMROW="${PREFIX}_${DAY_TMROW}"
#TABLE_YESDY="${PREFIX}_${DAY_YESDY}"




Q="INSERT INTO  $TABLE_AGGREGATED (date, dateTime, packetDeltaCount,  octetDeltaCount, direction, operator, protocolIdentifier)  	\
    select   date,  toStartOfHour(dateTime) t,  sum(packetDeltaCount), sum(octetDeltaCount), direction, operator, protocolIdentifier 	\
    from $TABLE_FULL  where t = toStartOfHour(now())-3600									\
    group by  date, t,  direction, operator, protocolIdentifier										\
    order by t, operator, direction"


Q_CREATE_NEXT_DAY=" \
CREATE TABLE IF NOT EXISTS $TABLE_FULL	\
(					\
date Date,                     		\
dateTime DateTime,              	\
duration UInt64,            		\
packetDeltaCount        UInt64,		\
octetDeltaCount         UInt64, 	\
egressInterface         String,		\
destinationTransportPort UInt32,	\
sourceTransportPort      UInt32,    	\
protocolIdentifier       String,  	\
destinationIPv4Address   String,	\
sourceIPv4Address        String,	\
ingressInterface         String,	\
sourceIPv4PrefixLength   String,	\
destinationIPv4PrefixLength  String,	\
bgpSourceAsNumber            UInt32,	\
bgpDestinationAsNumber       UInt32,	\
direction                 String,	\
operator                  String	\
)					\
ENGINE = MergeTree(date, (dateTime),8192);"


Q_DROP_PREV_DAY="DROP TABLE IF EXISTS $TABLE_FULL"


# aggregating data for previous hour
clickhouse-client --port 9008 --query="$Q"
echo $Q

#  3. if time > 0:00 && < 01:00 - create if not exist table for next_day, drop previous
date_h=`date +'%H'`
if [[ "$date_h" -gt 0 &&  "$date_h" -lt 1   ]]
then
    clickhouse-client --port 9008 --query=$Q_DROP_PREV_DAY
    clickhouse-client --port 9008 --query=$Q_CREATE_NEXT_DAY
fi



