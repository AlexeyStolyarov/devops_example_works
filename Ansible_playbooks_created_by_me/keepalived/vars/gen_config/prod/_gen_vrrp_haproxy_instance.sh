#!/bin/bash

# $1 = last octet of IP address 
# $2 = mysql-instance name

INSTANCE=$2
DICT_NAME="keepalived_vrrp_10_20_17_${1}_${2}"

IP="10.20.17.$1"
ID=$1
PASS="17$1"

# h28
s1_IP='10.20.16.27'
s1_IF='em1.216'
# h27
s2_IP='10.20.16.28'
s2_IF='em1.216'



cat <<END
---


${DICT_NAME}:
  name: ${DICT_NAME}
  id: ${ID}
  ip: ${IP}/23
  track_script: chk_ip #sphinx  #chk_nginx # chk_bind9
  password: ${PASS}

  keepalived_server_list:
 
  - ip_management: ${s1_IP}
    keepalived_vrrp_dev: ${s1_IF}
    keepalived_vrrp_role: BACKUP
    keepalived_vrrp_priority: 15
    dont_make_script_check: yes

  - ip_management: ${s2_IP}
    keepalived_vrrp_dev: ${s2_IF}
    keepalived_vrrp_role: MASTER
    keepalived_vrrp_priority: 40
#    dont_make_script_check: yes


END




