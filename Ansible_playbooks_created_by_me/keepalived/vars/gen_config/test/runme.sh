

for i in `cat ./instances.txt`; do 
IP=`echo $i | cut -d ':' -f1`
ID=`echo $i | cut -d ':' -f2`

    ./_gen_vrrp_haproxy_instance.sh $IP $ID  > ../out/vrrp_mysql_${ID}_192.168.99.$IP.yml

done
