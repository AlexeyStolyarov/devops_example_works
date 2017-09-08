#!/bin/bash

# $1 = last octet of IP address 
# $2 = mysql-instance name

INSTANCE=$2
DICT_NAME="keepalived_vrrp_192_168_99_${1}_${2}"

IP="192.168.99.$1"
ID=$1
PASS="99$1"

#deli2
s1_IP='deli2.dev.rugion.ru'
s1_IF=p'5p1'
#bkk
s2_IP='bkk.dev.rugion.ru'
s2_IF='eth0'



cat <<END
---


${DICT_NAME}:
  name: ${DICT_NAME}
  id: ${ID}
  ip: ${IP}/24
  track_script: chk_sphinx  #chk_nginx # chk_bind9
  password: ${PASS}

  keepalived_server_list:
 
  #deli2
  - ip_management: ${s1_IP}
    keepalived_vrrp_dev: ${s1_IF}
    keepalived_vrrp_role: BACKUP
    keepalived_vrrp_priority: 20
    dont_make_script_check: yes

  #bkk
  - ip_management: ${s2_IP}
    keepalived_vrrp_dev: ${s2_IF}
    keepalived_vrrp_role: MASTER
    keepalived_vrrp_priority: 40
    dont_make_script_check: yes


END




