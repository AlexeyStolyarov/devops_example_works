#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
import commands
import socket
import time
    
try:
        import collectd
except:
        import collectd_tools.collectd_mockup    as collectd

from haproxy_modules.haproxy     import haproxy
from haproxy_modules.tools.data_list import data_gathered
from haproxy_modules.tools.data_list import data_stat_index


PLUGIN_NAME     = "haproxy" #os.path.basename(__file__).split(".")[0]
stats           = haproxy.HAProxyStats('/var/run/haproxy/haproxy.sock')
VERBOSE_LOGGING = True

# convert list of "arg: val" to dict[arg]=val
def str2dict(arg):
    rez = {}
    for x in arg:
        if x:
            rez[(x.split(':')[0]).strip()] = x.split(':')[1].strip()

    return rez

def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('haproxy plugin [verbose]: %s' % msg)




# callback funcion for collectd Daemon
def read_callback(data=None):
        metric = collectd.Values()

        #
        # get Haproxy stat info
        #
#        rez = str2dict(stats.execute('show info'))
        #instance = rez['node']    or socket.gethostname()
        # loop over keys that we need
#        for i in    data_gathered['info']:
#            
#            metric.plugin = PLUGIN_NAME 
#            metric.interval = 60
#            metric.plugin_instance = instance 
#            metric.type = 'status'    
#            metric.type_instance = i            
#            metric.values = (unicodedata.numeric(rez[i]),)    #values must be list or tuple
#            metric.dispatch()

        # 
        # get stat info
        #
        f_ends = {}
        b_ends = {}
        b_ends_summ = {}
        for x in stats.execute('show stat'):
    
            # skiping some trash
            if x.startswith("#"):
                continue
            if x.startswith("stats"):
                continue
            if x == '':
                continue
    
            # convert string into array
            tmp = x.split(',')

            # fill frontends
            if tmp[1] == 'FRONTEND':
                f_ends[tmp[0]] = tmp
                continue
    
            # fill backend summary info
            if tmp[1] == 'BACKEND':
                #b_ends_summ[tmp[0]] = tmp
                continue
    
            # fill backen workers info
            b_ends["%s@%s" % (tmp[1],tmp[0])] = tmp




        # fill data for backends
        for z in data_gathered['stat']:
            # fill info for backend/workers
            for k, v    in b_ends.iteritems():
                # skip empty values
                if v[data_stat_index[z]]:
                    metric.plugin = PLUGIN_NAME
                    metric.interval = 60
        
                    metric.plugin_instance = v[0] 
                    metric.type =  z
                    metric.type_instance = k.split('_')[0]
        
                    metric.values = (v[data_stat_index[z]],) #values must be list or tuple
                    #collectd.info('p:' +  metric.plugin + ' pi:' + metric.plugin_instance + ' t:' + metric.type + ' ti:' + metric.type_instance
                    #               + ' v:' + metric.values)
                    metric.dispatch()

            for k, v    in f_ends.iteritems():
                # skip empty values
                if v[data_stat_index[z]]:
                    metric.plugin = PLUGIN_NAME 
                    metric.interval = 60

                    metric.plugin_instance = v[0] 
                    metric.type =   z
                    metric.type_instance = "FE"
                                
                    metric.values = (v[data_stat_index[z]],) #values must be list or tuple
                    #collectd.info('p:' +  metric.plugin + ' pi:' + metric.plugin_instance + ' t:' + metric.type + ' ti:' + metric.type_instance
                    #               + ' v:' + metric.values)
                    metric.dispatch()




#for debugging purposes
#read_callback()

collectd.register_read(read_callback)

