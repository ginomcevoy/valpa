import sys
import csv

def read_metrics(stdout, stderr, expDir):
    """ Read application metrics for the NPB-FT benchmark.
    
    The application-specific metrics are:
    - initTime (initialization time)
    - appTime (execution time seen by application)
    - mopsTotal (net throughput, million op/s)
    - mopsProc (throughput per process, million op/s)
    """
    
    # no custom file needed, desired output is in stdout
    lines = stdout.readlines()
    for line in lines:
        # look for initTime
        if 'Initialization time' in line:
            initTime = float(line.split('=')[1])
            initTime = round(initTime, 3) # avoid long decimals
        
        # look for appTime
        if 'Time in seconds' in line:
            appTime = float(line.split('=')[1])
            
        # look for mopsTotal
        if 'Mop/s total' in line:
            mopsTotal = float(line.split('=')[1])
            
        # look for mopsProc
        if 'Mop/s/process' in line:
            mopsProc = float(line.split('=')[1])
            
    items = (('initTime', initTime), ('appTime', appTime), 
             ('mopsTotal', mopsTotal), ('mopsProc', mopsProc))
    return OrderedDict(items)
