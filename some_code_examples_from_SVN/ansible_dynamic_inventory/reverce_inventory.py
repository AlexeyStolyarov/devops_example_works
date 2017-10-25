#!/usr/bin/env python
#
# sctipt treates sys.argv[1]  as ansible inventoty file, reverces hosts in group_name and put it in sys.argv[2] file
#
#  how to use:
#
# if [[ "$COMMAND" == "stop" ]]
# then
#    INV_TEMP=`mktemp`
#    "$MY_BASE/lib/python/inv_reverse.py" "$INV" "$INV_TEMP"
#    INV=$INV_TEMP
# fi



import sys

#print 'Argument List:', sys.argv[1], sys.argv[2]

inv = {}
current_key = ''

for line in open(sys.argv[1]):
    li=line.strip()
    if not li:
        continue

    if not li.startswith("#"):
        if li.startswith("["):
            #we have group_name
            current_key=li
            inv[current_key] = []
        else:
            #we have hosts
            inv[current_key].append(li)


f = open(sys.argv[2], 'w')
for k,v in inv.iteritems():
    f.write(k)
    f.write("\n")

    for x in v[::-1]:
        f.write(x)
        f.write("\n")

f.close()
