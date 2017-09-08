=Original git repo
https://github.com/CESNET/ipfixcol

when trying to build Docker image it produces error "cannot find SSL library"
just use --without-openssl in dockerfile.

=to put parsed data into ClickHouse you need to create

```
CREATE TABLE default.nflow_full
(

date Date,                      --  flowStartMilliseconds
dateTime DateTime,              -- flowStartMilliseconds
duration UInt64,                -- (flowEndMilliseconds - flowStartMilliseconds)
packetDeltaCount        UInt64,
octetDeltaCount         UInt64, 
egressInterface         String,
destinationTransportPort UInt32,
sourceTransportPort      UInt32,
protocolIdentifier       String,
destinationIPv4Address   String,
sourceIPv4Address        String,
ingressInterface         String,
sourceIPv4PrefixLength   String,
destinationIPv4PrefixLength  String,
bgpSourceAsNumber            UInt32,
bgpDestinationAsNumber       UInt32,
direction                 String,
operator                  String
)

ENGINE = MergeTree(date, (dateTime),8192);



-- aggregation and size reducing

CREATE TABLE default.nflow_aggreg
(
date                Date,
dateTime            DateTime,
packetDeltaCount    UInt64,
octetDeltaCount     UInt64,
direction           String,
operator            String,
protocolIdentifier  String
)

ENGINE = MergeTree(date, (operator),8192);

```




=to better perfomance and less hard disk wasting a good idea is to keep temporary json files in ram disk
modprobe zram num_devices=1 
echo 2048M > /sys/block/zram0/disksize 
mkfs.ext2 /dev/zram0 
mount /dev/zram0 /mnt/volumes/IPFIX2ClickHouse

