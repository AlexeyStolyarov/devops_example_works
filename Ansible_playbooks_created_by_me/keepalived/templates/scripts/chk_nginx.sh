#!/bin/bash

curl --connect-timeout 2  --fail http://localhost/ > /dev/null 2>&1


rez=$?
if [[ $rez == 22 ]]
    then
        exit 0
elif [[ $rez == 0 ]]
    then
        exit 0
else
        exit 99
fi



