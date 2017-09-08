#!/bin/bash

resp=`dig @localhost localhost +time=2  +tries=1 | grep localhost |  grep 127.0.0.1 | awk '{print $5}'`


if [[ $resp == "127.0.0.1" ]]
    then
        exit 0
else
        exit 99
fi



