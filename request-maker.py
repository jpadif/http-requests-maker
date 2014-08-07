#!/usr/bin/python
import sys
import re
import threading
import time
from Queue import Queue

try:
  import requests
except:
  print 'Request module is not installed, execute "pip install requests" or go to: http://docs.python-requests.org/ for more info.'
  sys.exit(0)

  
def validateIterations(iterations):
  if not isinstance(iterations,float):
    print 'iterations must be a number'
    sys.exit(0)

def validateTarget(target):
  regex = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  if not regex.match(target):
    print 'The target is not valid'
    sys.exit(0)

def make_call(url, queue, no):
  no = str(no)
  print 'Starting call #'+no + '\n'
  start = time.time()
  r = requests.get(url)
  elapsed = (time.time() - start)
  s_code = r.status_code
  print 'Call #'+no+' completed. Elapsed: ' + str(elapsed) + 'with status code of: ' + str(s_code)  + '\n'
  result = {'time':elapsed,'text':r.text, 's_code':s_code}
  queue.put(result)
  


def main(arguments):
  # Check if arguments are supplied
  if len(arguments) < 4:
    print 'Usage test.py <iterations> <execution time in seconds> <Target url>'   
    sys.exit(0)

  iterations   = float(arguments[1])
  exec_time    = float(arguments[2])
  target       = arguments[3]
  it_per_second =  exec_time / iterations

  


  # Validate user input 
  validateIterations(iterations)
  validateIterations(exec_time)
  validateTarget(target)
  print '--------------------------------------------------------------'
  print 'Making one petition every '+str(it_per_second)+' to: '+target + ' total: ' +str(iterations)+ ' iterations'
  print '--------------------------------------------------------------'
  queue = Queue()
  thread_results = []
  thread_pool = []

  for n in range(0,int(iterations)):
    thread_pool.append(threading.Timer(it_per_second * n,make_call,[target,queue,n]))

  for thread in thread_pool:
    thread.start()


  for thread in thread_pool:
    response = queue.get()
    thread_results.append(response)
    thread.join()
  parse_results(thread_results)
  
def parse_results(results_list):
  print '----------------------------------------------'
  total  = 0.0
  r_type = {'200':0,'400':0}
  min_time = None
  max_time = None
  
  for result in results_list:
    time = float(result['time'])
    total = (total + time)
    r_type[result['s_code']] = 1 

    # Get min time
    if min_time is not None:
      min_time = time if time < min_time else min_time
    else:
      min_time = time

    # Get max time
    if max_time is not None:
      max_time = time if time > max_time else max_time
    else:
      max_time = time

  avg = total / len(results_list)
  data = (avg,max_time,min_time)
  print 'Average time of response: {0} max time: {1} min time: {2}'.format(*data)



#------------------------------------------------------------
main(sys.argv)
