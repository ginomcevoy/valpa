'''
Created on Sep 21, 2014
 
@author: giacomo
'''
from .enum import PinningOpt

class SimpleRules(object):
    '''
    Rules for defining cluster placements using the simple characterization, 
    using the DIST tuple:
    nc: number of cores in virtual cluster
    cpv: cores per VM
    idf: inverse of distribution factor df,
    idf = 0, if cluster is in a single PM
        = vpm (virtual cores per PM), if cluster is in more than one PM
    pstrat = one of the available pinning strategies
    The rules focus on the first three variables.
    '''

    def __init__(self, hwSpecs):
        '''
        Constructor, receives hardware specs 
        '''
        self.hwSpecs = hwSpecs
        
    def isNcPermitted(self, nc):
        '''
        Returns True iff the nc value is fit for the hardware,
        nc positive integer and nc less than / equal to the total available physical cores
        '''
        return type(nc) == type(1) and nc > 0 and nc <= self.hwSpecs['coresInCluster']
    
    def isCpvPermitted(self, cpv):
        '''
        Returns True iff the cpv value is fit for the hardware,
        cpv positive and cpv less than / equal to physical cores in a PM
        '''
        return type(cpv) == type(1) and cpv > 0 and cpv <= self.hwSpecs['cores'] 
    
    def isIdfPermitted(self, idf):
        '''
        Returns True iff the idf value is fit for the hardware:
        idf = 0 (single PM) and idf = -1 (physical cluster) are always
        allowed; other values require multiple available PMs and 
        idf <= the physical cores in a PM.
        idf -1 for physical cluster, idf 0 for 1 PM, idf less than / 
        equal to physical cores in a PM
        '''
        multiplePMs = self.hwSpecs['nodes'] > 1
        idfForMultipleAllowed = (idf > 0 and idf <= self.hwSpecs['cores'] and
                                 multiplePMs)
        includesPermitted = idf == -1 or idf == 0 or idfForMultipleAllowed
        return type(idf) == type(1) and includesPermitted
    
    def isPstratPermitted(self, pstrat):
        '''
        Returns True iff the pstrat value is one of the available options.
        '''
        return pstrat in allPstrats()
    
    def allCpvGivenNc(self, nc):
        '''
        Returns list of cpv values that are admitted given the hardware and
        a virtual cluster size. Returns empty if nc is not permitted.
        '''
        if not self.isNcPermitted(nc):
            return []
        
        # rule 1: cpv should divide nc
        # rule 2: cpv cannot exceed physical cores in a PM
        # get all divisors of nc, then apply rule 2 from isCpvPermitted
        cpvs = divisorsOf(nc, self.hwSpecs['cores'])
        for cpv in cpvs:
            if not self.isCpvPermitted(cpv):
                cpvs.remove(cpv)
        
        return cpvs
    
    def allCpvGivenIdf(self, idf):
        '''
        Returns list of cpv values that are admitted given the hardware and
        idf value. Returns empty if idf is not permitted.
        '''
        if not self.isIdfPermitted(idf):
            return []
        
        # rule 1: idf > 0, cpv should divide idf
        # rule 2: if idf = 0 or idf = -1, then cpv gets all values up to physical cores in a PM
        # idf already valid at this point, generate according to pertinent rule
        if idf > 0:
            cpvs = divisorsOf(idf)
        else:
            cpvs = list(range(1, self.hwSpecs['cores'] + 1))
        
        return cpvs
    
    def allIdfGivenNc(self, nc):
        '''
        Returns list of idf values that are admitted given the hardware and
        nc value. Skips idf = -1 (virtual clusters only). 
        Returns empty if nc is not permitted.
        '''
        if not self.isNcPermitted(nc):
            return []
        
        # rule 1: For idf > 0, idf should divide nc, but not equal to it
        # rule 2: idf cannot exceed number of physical cores in PM
        # rule 3: For idf to be small (spread VMs), there should be enough PMs        
        # rule 4: if nc fits in a PM, add idf = 0
        
        # find divisors of nc (rule 1) constrained to rule 2
        idfCandidates = divisorsOf(nc, self.hwSpecs['cores'])
        if nc in idfCandidates:
            idfCandidates.remove(nc)
        
        # filter the low end according to rule 3
        minIdf = nc * 1.0 / self.hwSpecs['nodes']
        if minIdf > 1:
            idfs = removeLowerEqualsThan(idfCandidates, minIdf)
        else:
            idfs = idfCandidates
            
        # add idf = 0 if possible (rule 4)
        if nc <= self.hwSpecs['cores']:
            idfs.insert(0, 0)
                            
        return idfs
    
    def allIdfGivenCpv(self, cpv):
        '''
        Returns list of idf values that are admitted given the hardware and
        cpv value. Skips idf = -1 (virtual clusters only). 
        Returns empty if cpv is not permitted.
        '''
        if not self.isCpvPermitted(cpv):
            return []
        
        # rule 1: idf is a multiple of cpv up to the number of physical 
        # cores, if there is more than one PM
        # rule 2: always consider idf = 0 for this evaluation
        if self.hwSpecs['nodes'] > 1:
            idfs = multiplesOf(cpv, self.hwSpecs['cores'])
        else:
            idfs = []
        idfs.insert(0, 0)
        return idfs
    
    def allCpvGiven(self, nc, idf):
        '''
        Returns list of cpv values that are admitted given the hardware and
        nc/idf values.
        '''
        # nc should be allowed before proceeding
        if not self.isNcPermitted(nc):
            return []
        
        # idf should be allowed before proceeding
        if idf not in self.allIdfGivenNc(nc):
            return []
        
        ncList = self.allCpvGivenNc(nc)
        idfList = self.allCpvGivenIdf(idf) 
        return mergeLists(ncList, idfList)
    
    def allIdfGiven(self, nc, cpv):
        '''
        Returns list of idf values that are admitted given the hardware and
        nc/cpv values.
        '''
        # nc should be allowed before proceeding
        if not self.isNcPermitted(nc):
            return []
        
        # cpv should be allowed before proceeding
        if cpv not in self.allCpvGivenNc(nc):
            return []
        
        ncList = self.allIdfGivenNc(nc)
        cpvList = self.allIdfGivenCpv(cpv) 
        return mergeLists(ncList, cpvList)
    
    def allNcGivenCpv(self, cpv):
        '''
        Returns list of nc values that are admitted given the hardware and
        a VM size. Returns empty if cpv is not permitted.
        '''
        if not self.isCpvPermitted(cpv):
            return []
        
        # rule 1: nc should be multiple of cpv
        # rule 2: nc cannot exceed available cores in physical cluster
        # rule 3: given nc and cpv, at least one idf should exist
        
        # multiplesOf helper function can be used for rules 1 and 2
        candidateNcs = multiplesOf(cpv, self.hwSpecs['coresInCluster'])
        ncs = []
        for nc in candidateNcs:
            idfs = self.allIdfGiven(nc, cpv)
            if len(idfs) > 0:
                # rule 3 - at least one valid idf
                ncs.append(nc)
        
        return ncs
    
    def allNcGivenIdf(self, idf):
        '''
        Returns list of nc values that are admitted given the hardware and
        a idf value. Returns empty if idf is not permitted.
        '''
        if not self.isIdfPermitted(idf):
            return []
        
        # rule 1: if idf=0, nc should be less/equal cores in PM
        # rule 2: if idf > 0, nc should be multiple of idf 
        # rule 3: if idf > 0, need more than one, and enough physical machines
        # rule 4: if idf == -1, nc should fit in physical cluster and have valid cpv
        
        if idf == 0:
            # rule 1
            ncs =  list(range(1, self.hwSpecs['cores'] + 1))
            
        elif idf > 0:
            # rule 2
            candidateNcs = multiplesOf(idf, self.hwSpecs['coresInCluster'])
            ncs = []
            # rule 3
            for nc in candidateNcs:
                physicalMachines = nc / idf
                if physicalMachines > 1 and physicalMachines <= self.hwSpecs['nodes']:
                    ncs.append(nc)
            
        else: # only idf = -1 left
            # rule 4
            candidateNcs = list(range(1, self.hwSpecs['coresInCluster'] + 1))
            ncs = []
            for nc in candidateNcs:
                cpvs = self.allCpvGiven(nc, idf)
                if len(cpvs) > 0:
                    ncs.append(nc)
            
        return ncs
    
    def allNcGiven(self, cpv, idf):
        '''
        Returns list of nc values that are admitted given the hardware and
        cpv/idf values.
        '''
        # cpv should be allowed before proceeding
        if not self.isCpvPermitted(cpv):
            return []
        
        # idf should be allowed before proceeding
        if idf not in self.allIdfGivenCpv(cpv):
            return []
        
        cpvList = self.allNcGivenCpv(cpv)
        idfList = self.allNcGivenIdf(idf)
        return mergeLists(cpvList, idfList)
    
    def allPstratGiven(self, nc, cpv, idf):
        '''
        Returns list of PinningOpt values that are admitted given the hardware and
        cpv value.
        '''
        # strategies overlap on the following scenarios: 
        # a) with cpv = 1, BAL-ONE == BAL-SET == SPLIT; 
        # b) with one VM per machine or using 100% of machine, BAL-ONE === GREEDY; 
        # c) with cpv = pcores, BAL-ONE === SPLIT.
        # SPLIT is not allowed for odd cpvs (d)  
        
        #PinningOpt = Enum(["BAL_ONE", "BAL_SET", "GREEDY", "SPLIT", "NONE"])
        pstrats = allPstrats()

        if cpv == 1:
            # scenario a)
            pstrats.remove(PinningOpt.BAL_SET)
            pstrats.remove(PinningOpt.SPLIT)
        if cpv == idf or nc == cpv or idf == self.hwSpecs['cores']:
            # scenario b)
            pstrats.remove(PinningOpt.GREEDY)
        if cpv == self.hwSpecs['cores']:
            # scenario c)
            pstrats.remove(PinningOpt.SPLIT)
        if cpv % 2 == 1 and PinningOpt.SPLIT in pstrats:
            # scenario d)
            pstrats.remove(PinningOpt.SPLIT)
            
        return pstrats
    
    def canBeDeployedExactly(self, nc, idf, physicalMachines):
        '''
        Returns True iff the virtual cluster can be deployed in exactly the
        amount of physicalMachines specified. Does not apply for physical
        cluster.
        '''
        if idf == -1:
            raise ValueError("Only virtual clusters!")
        
        # nc/idf should be possible
        possibleIdfs = self.allIdfGivenNc(nc)
        if idf not in possibleIdfs:
            return False
        
        if idf == 0:
            # implies single PM
            return physicalMachines == 1
        else:
            return physicalMachines == nc / idf
        
    def canBeDeployedInAny(self, nc, idf, physicalMachinesTuple):
        '''
        Returns True iff the virtual cluster can be deployed in any of the
        amount of physicalMachines specified. Does not apply for physical
        cluster.
        '''
        canBeDeployed = False
        for physicalMachines in physicalMachinesTuple:
            if self.canBeDeployedExactly(nc, idf, physicalMachines):
                canBeDeployed = True
                break
            
        return canBeDeployed
           
# Helper functions
           
def divisorsOf(value, limit=None):
    '''
    Finds divisors of an integer, up to an optional limit. If value is
    within limit, it is included in the list.
    @return: list of divisors
    '''
    if limit is None:
        limit = value
        
    nextDivisor = 1
    divisors = []
    while nextDivisor <= limit:
        if value % nextDivisor == 0:
            divisors.append(nextDivisor)
        nextDivisor = nextDivisor + 1
    return divisors

def multiplesOf(value, limit):
    '''
    Finds multiples of an integer (including said value), up to a limit. 
    If value exceeds the limit, returns an empty list.
    @return: list of multiples
    '''
    if value > limit:
        return []
    
    result = []
    candidate = value
    while candidate <= limit:
        if candidate % value == 0:
            result.append(candidate)
        candidate = candidate + 1
    return result

def removeLowerEqualsThan(values, minValue):
    result = []
    for val in values:
        if val >= minValue:
            result.append(val)
    return result

def mergeLists(list1, list2):
    result = []
    for val in list1:
        if val in list2:
            result.append(val)
    return result

def allPstrats():
    return set([PinningOpt.BAL_ONE, PinningOpt.BAL_SET, PinningOpt.GREEDY, PinningOpt.SPLIT, PinningOpt.NONE])