import sys
import csv
from collections import OrderedDict

def read_metrics(stdout, stderr, expDir, customFile):
    """ Read application metrics for the Parpac benchmark.
    
    The application-specific metrics are:
    - appTime (execution time)
    - fluidRate (throughput in application metric)
    - floatRate (throughput in Gflops)
    """
    
    # Only the secondary output is relevant for the metrics
    # Vespa should pass the secondary output as an open customFile
    customText = customFile.read()
    
    # Look for line with AppTime
    appTimeIndex = customText.find('total simulation time')
    hasInfo = customText[appTimeIndex:len(customText)]
    splits = hasInfo.split(':')

    # AppTime is in the first line (second block)
    appTime = splits[1].split('\n')[0].split(' ')[1]
    appTime = float(appTime)

    # FluidRate is in the second line (third block)
    fluidRate = splits[2].split('\n')[0].split(' ')[1]
    fluidRate = float(fluidRate)

    # FloatRate is in the third line (fourth block)
    floatRate = splits[3].split('\n')[0].split(' ')[1]
    floatRate = float(floatRate)
     
    items = (('appTime', appTime),
             ('fluidRate', fluidRate),
             ('floatRate', floatRate)
             )
    return OrderedDict(items)
