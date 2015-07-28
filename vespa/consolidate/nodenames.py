'''
Created on Mar 12, 2013

@author: Giacomo Mc Evoy
'''

import sys
import re

def run():
    
    # Read filename from args
    filename = sys.argv[1]

    # open file and read it
    aFile = open(filename, 'r')
    text = aFile.read()
    
    # get the repeated filenames
    repeatedNames = re.split('\\n', text)
    
    # work on repeated filenames
    names = unique(repeatedNames)

    # output to another file
    outputName = sys.argv[2]
    output = open(outputName, 'w')
    writeNames(output, names)
    
def unique(repeatedNames):
    uniques = []
    
    # boundary condition: empty list
    if len(repeatedNames) == 0:
        return uniques
    
    # sort makes things easier
    repeatedNames = sorted(repeatedNames)

    # add the rest
    for s in repeatedNames:

        # condition of empty name (due to split)
        if len(s) == 0:
            continue

        # boundary condition for first element 
        if len(uniques) == 0:
            uniques.append(s)
            continue
        
        # add the rest 
        size = len(uniques)
        if uniques[size - 1] != s:
            # this node name has not been added yet
            uniques.append(s);
        
    return uniques;

def writeNames(output, names):
   
    for name in names:
        output.write(name + '\n')
    output.close()

# Do this when attempting to submit module
if __name__ == '__main__':
    run()
