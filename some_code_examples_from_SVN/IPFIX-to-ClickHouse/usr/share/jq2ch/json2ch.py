#!/usr/bin/python

import json
import sys
from datetime import datetime

if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s json.file_to_parce \n" %  sys.argv[0],)
    sys.exit(1)
jsonfile=sys.argv[1]

debug=0

with open(jsonfile) as fp:

    # taking desision based on input_interface and output_interface which together are hash key.  i.e. input nexthop_switcher["input"_"output"] => direction
    #   Logical interface xe-0/0/3.600 (Index 343) (SNMP ifIndex 629)  - E1
    #   Logical interface xe-0/0/0.0 (Index 347) (SNMP ifIndex 606)    - TTK
    #   Logical interface irb.200 (Index 340) (SNMP ifIndex 603)       - internal
    #   Logical interface irb.416 (Index 402) (SNMP ifIndex 640)       - VokrugSveta

    
    def nexthop_switcher(arg_in, arg_out):

        caser={
        "629": "E1",
        "606": "TTK",
        "603": "Rugion",
        "640": "VokrugSveta"
        }


        direction = "UNKNOWN: %s=>%s" % (arg_in,arg_out)
        operator  = "UNKNOWN"

        if "629" in arg_in  or  "606" in arg_in:
            direction = "in"
            operator  = caser.get(arg_in)
        else: 
            direction = "out"
            operator  = caser.get(arg_out)

        return (direction, operator)



    for line in iter(fp.readline, ''):

	json_var=json.loads(line)

#	print line
	#flowStartMilliseconds => 2017-08-31T10:33:57.745
	if not json_var.has_key("flowStartMilliseconds") or not json_var.has_key("flowEndMilliseconds"):
		continue

	tmp_st  =  datetime.strptime(json_var["flowStartMilliseconds"].split(".")[0], '%Y-%m-%dT%H:%M:%S')
	tmp_end =  datetime.strptime(json_var["flowEndMilliseconds"].split(".")[0], '%Y-%m-%dT%H:%M:%S')
	duration =  int( (tmp_end - tmp_st).total_seconds() )

	direction, operator = nexthop_switcher(str(json_var['ingressInterface']),  str(json_var['egressInterface'])  )

	tmp_date  =  tmp_st.strftime('%Y-%m-%d')
	tmp_date2  =  tmp_st.strftime('%Y-%m-%d %H:%M:%S')
	csv = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"  \
	    % (tmp_date,tmp_date2,duration, 
		json_var['packetDeltaCount'],
		json_var['octetDeltaCount'],
		json_var['egressInterface'],
		json_var['destinationTransportPort'],
		json_var['sourceTransportPort'],
		json_var['protocolIdentifier'],
		json_var['destinationIPv4Address'],
		json_var['sourceIPv4Address'],
		json_var['ingressInterface'],
		json_var['sourceIPv4PrefixLength'],
		json_var['destinationIPv4PrefixLength'],
		json_var['bgpSourceAsNumber'],
		json_var['bgpDestinationAsNumber'],
		direction, operator
	      )
	if debug:
		str_debug = """tmp_date: %s, tmp_date2: %s, duration: %s, packetDeltaCount: %s,octetDeltaCount: %s,egressInterface: %s,destinationTransportPort: %s,sourceTransportPort: %s,  \
			    protocolIdentifier: %s,destinationIPv4Address: %s,sourceIPv4Address: %s,ingressInterface: %s,sourceIPv4PrefixLength: %s,destinationIPv4PrefixLength: %s,  \
			    bgpSourceAsNumber: %s,bgpDestinationAsNumber%s,direction,: %s,operator: %s """ \
		% (tmp_date,tmp_date2,duration, 
		json_var['packetDeltaCount'],
		json_var['octetDeltaCount'],
		json_var['egressInterface'],
		json_var['destinationTransportPort'],
		json_var['sourceTransportPort'],
		json_var['protocolIdentifier'],
		json_var['destinationIPv4Address'],
		json_var['sourceIPv4Address'],
		json_var['ingressInterface'],
		json_var['sourceIPv4PrefixLength'],
		json_var['destinationIPv4PrefixLength'],
		json_var['bgpSourceAsNumber'],
		json_var['bgpDestinationAsNumber'],
		direction, operator
	      )
		print  str_debug
	else:
		print csv
