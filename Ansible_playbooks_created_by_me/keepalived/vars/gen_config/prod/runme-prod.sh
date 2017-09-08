

for i in `cat ./instances-prod.txt`; do 
IP=`echo $i | cut -d ':' -f1`
ID=`echo $i | cut -d ':' -f2`

    ./_gen_vrrp_haproxy_instance.sh $IP $ID  > ../out/vrrp_mysql_${ID}_10.20.17.$IP.yml

done
