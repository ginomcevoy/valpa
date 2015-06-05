'''
Created on Oct 17, 2013

@author: giacomo
'''
import subprocess
    
def newUUID(forReal=True):
    '''
    Creates a UUID. if forReal is false, then it creates a static string, useful
    for testing.
    '''
    if forReal:
        output = subprocess.check_output(['uuidgen'])
        return output.decode('utf-8')[0:len(output) -1]
    else:
        return '446bf85f-b4ba-459b-8e04-60394fc00d5c'