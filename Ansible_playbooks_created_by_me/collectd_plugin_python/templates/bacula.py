import collectd
import os
import socket
import time
import subprocess


bconsole_data = {}

bconsole_staus = {}
bconsole_staus['T']='Terminated normally'
#bconsole_staus['C']='Created but not yet running'
bconsole_staus['R']='Running'
bconsole_staus['B']='Blocked'
bconsole_staus['E']='Terminated in Error'
bconsole_staus['e']='Non-fatal error'
bconsole_staus['f']='Fatal error'
#bconsole_staus['D']='Verify Differences'
bconsole_staus['A']='Canceled by the user'
#bconsole_staus['F']='Waiting on the File daemon'
#bconsole_staus['S']='Waiting on the Storage daemon'
bconsole_staus['m']='Waiting for a new Volume to be mounted'
#bconsole_staus['M']='Waiting for a Mount'
#bconsole_staus['s']='Waiting for Storage resource'
#bconsole_staus['j']='Waiting for Job resource'
#bconsole_staus['c']='Waiting for Client resource'
#bconsole_staus['d']='Wating for Maximum jobs'
#bconsole_staus['t']='Waiting for Start Time'
#bconsole_staus['p']='Waiting for higher priority job to finish'


plugin_name = 'bacula-collectd'

def collect_data():

  global bconsole_staus
  global bconsole_data
  today = (time.strftime("%Y-%m-%d"))

  ps = subprocess.Popen( "ps -C bacula-dir | grep  bacula-dir", shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  bacula_dir_running = ps.communicate()[0].rstrip('\n')

  if bacula_dir_running:
    for i in bconsole_staus.keys():
  
      # get number of jobs for each bconsole_staus
      my_command = "echo 'list jobs' | bconsole  | grep %s  | cut -d '|' -f 9 | grep %s | wc -l " % (today,i)
  
      ps = subprocess.Popen(my_command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      output = ps.communicate()[0].rstrip('\n')
      bconsole_data[i]=output

  else:
  # if bacula-dir not running we make signals by -1 and try to restart bacula-dir
    for i in bconsole_staus.keys():
      bconsole_data[i]=-1
    ps = subprocess.Popen( "service bacula-director restart", shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

  return


def read_callback(data=None):

  global bconsole_staus
  global bconsole_data
  global fname, host_name

  collect_data()

  for k,v in bconsole_data.items():
#    collectd.warning ('%s=>%s!' % (k,v))
#    collectd.warning (plugin_name)    
#    collectd.warning (bconsole_staus[k] )    

    metric = collectd.Values()
    metric.plugin = plugin_name 
    metric.interval = 60
    metric.type = 'gauge'
    metric.type_instance = bconsole_staus[k]                  # text description of each value
    metric.values = (v,)
    metric.dispatch()


collectd.register_read(read_callback)

