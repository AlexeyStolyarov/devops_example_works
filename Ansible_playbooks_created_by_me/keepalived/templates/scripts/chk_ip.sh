#!/bin/bash

#
# 
# list of virtual_router_id numbers  that we want to change to backup state
# 
#
DOWN_IDS="9999 6000"

for i in $DOWN_IDS; do
    if [[ "$1" == "$i" ]]; then 
    exit 2
    fi
done


exit 0
