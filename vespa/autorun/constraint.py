'''
Created on Sep 26, 2014

@author: giacomo
'''
from bean.enum import PinningOpt
from bean.simple import SimpleRules

#  super(ParentClass, self).__init__(superParams)

# isinstance(simpleExpConstraintInstance, ExperimentConstraint)

class ClusterConstraint():
    '''
    Provides a constraint for possible virtual clusters that will be generated.
    '''

class SimpleClusterConstraint(ClusterConstraint):
    '''
    ClusterConstraint that uses the simple characterization of virtual clusters.
    Can only hold a single constraint (e.g. virtual cluster size OR VM size OR...)
    '''
        
    def __init__(self):
        self.alreadyDefined = False
        self.ncTuple = None
        self.cpvTuple = None
        self.idfTuple = None
        self.pstratSet = None
        self.physicalMachinesTuple = None
    
    def constrainNc(self, ncTuple):
        self.__checkState__()
        self.ncTuple = ncTuple
        self.alreadyDefined = True
        
    def constrainCpv(self, cpvTuple):
        self.__checkState__()
        self.cpvTuple = cpvTuple
        self.alreadyDefined = True
        
    def constrainIdf(self, idfTuple):
        self.__checkState__()
        self.idfTuple = idfTuple
        self.alreadyDefined = True
        
    def constrainPstrat(self, pstratSet):
        self.__checkState__()
        self.pstratSet = set(pstratSet)
        self.alreadyDefined = True
        
    def constrainPhysicalMachines(self, physicalMachinesTuple):
        self.__checkState__()
        self.physicalMachinesTuple = physicalMachinesTuple
        self.alreadyDefined = True
            
    def __checkState__(self):
        assert not self.alreadyDefined, "This constraint has already been defined, use another"
        
class ClusterGenerationSpecification():
    '''
    This specification interface can be used to determine which virtual clusters 
    may be constructed within a experiment generator. It provides the internal 
    state of a ClusterSet as a value object, that generates new instances of 
    itself as new constraints are added.
    '''
    
    def constrainWith(self, clusterConstraint):
        '''
        @return: ClusterConstraintSpecification that takes into account the 
        additional constraint provided
        '''
        pass 
    
    def intersectWith(self, clusterGenerationSpec):
        '''
        @return: ClusterGenerationSpecification that satisfies both the current
        and the provided specifications
        '''
        pass
    
    def mergeWith(self, clusterGenerationSpec):
        '''
        @return: ClusterGenerationSpecification that satisfies either the current
        or the provided specifications
        '''
        pass
    
class SimpleClusterGenerationSpecification(ClusterGenerationSpecification):
    '''
    ClusterGenerationSpecification that uses the simple virtual cluster
    characterization (SimpleRules). Initially, describes all possible virtual 
    clusters, but can be constrained incrementally for less virtual clusters.
    Pstrat is considered separately (not part of the combinatorial space), so
    all nc/cpv/idf combinations will get the same pstrats (as long as the DIST tuple
    satisfies the simple specification). 
    '''
    
    def __init__(self, hwSpecs, internalSpace = None, pstrats = None):
        self.hwSpecs = hwSpecs
        self.simpleRules = SimpleRules(hwSpecs)
        
        if internalSpace is None:
            # {nc1 : set([(cpv, idf), (cpv, idf), ...]), nc2 : set([...]), ... } 
            self.__buildInternalSpace__()
        else:
            self.internalSpace = internalSpace
            
        if pstrats is None:
            self.pstrats = set([PinningOpt.BAL_ONE, PinningOpt.BAL_SET, PinningOpt.GREEDY, PinningOpt.SPLIT, PinningOpt.NONE])
        else:
            self.pstrats = pstrats
    
    def constrainWith(self, clusterConstraint):
        # valid simple constraint
        assert isinstance(clusterConstraint, SimpleClusterConstraint)
        assert clusterConstraint.alreadyDefined, "Cluster constraint undefined" 
        
        # Probe constraint type. Given the type, process the space and return a new
        # specification object with the updated space. Constraint is guaranteed to be
        # of a single type only
        if clusterConstraint.ncTuple is not None:
            constrainedSpace = self.__constrainWithNc__(clusterConstraint.ncTuple)
        if clusterConstraint.cpvTuple is not None:
            constrainedSpace = self.__constrainWithCpv__(clusterConstraint.cpvTuple)
        if clusterConstraint.idfTuple is not None:
            constrainedSpace = self.__constrainWithIdf__(clusterConstraint.idfTuple)
        if clusterConstraint.physicalMachinesTuple is not None:
            constrainedSpace = self.__constrainWithPhysicalMachines__(clusterConstraint.physicalMachinesTuple)
            
        # pstrat is considered separately
        if clusterConstraint.pstratSet is not None:
            constrainedPstrat = self.pstrats.intersection(clusterConstraint.pstratSet)
            
            # if this branch executes, constrainedSpace was not defined until now
            constrainedSpace = self.internalSpace
        else:
            constrainedPstrat = self.pstrats
        
        return SimpleClusterGenerationSpecification(self.hwSpecs, constrainedSpace, constrainedPstrat)
        
    def intersectWith(self, clusterGenerationSpec):
        # valid simple cluster generation spec
        assert isinstance(clusterGenerationSpec, SimpleClusterGenerationSpecification)
        
        otherSpace = clusterGenerationSpec.internalSpace
        intersectedSpace = {}
        
        # find common ncs
        for nc in self.internalSpace.keys():
            if nc in otherSpace.keys():
                # common nc, intersect both cpv/idf sets
                thisNcSet = self.internalSpace[nc]
                otherNcSet = otherSpace[nc]
                intersectedNcSet = thisNcSet.intersection(otherNcSet)
                intersectedSpace[nc] = intersectedNcSet
                
        # intersect pstrats
        intersectedPstrats = self.pstrats.intersection(clusterGenerationSpec.pstrats)
                
        return SimpleClusterGenerationSpecification(self.hwSpecs, intersectedSpace, intersectedPstrats)
    
    def mergeWith(self, clusterGenerationSpec):
        # valid simple cluster generation spec
        assert isinstance(clusterGenerationSpec, SimpleClusterGenerationSpecification)
        
        otherSpace = clusterGenerationSpec.internalSpace
        mergedSpace = {}
        
        # find common ncs
        for nc in self.internalSpace.keys():
            if nc in otherSpace.keys():
                # common nc, union both cpv/idf sets
                thisNcSet = self.internalSpace[nc]
                otherNcSet = otherSpace[nc]
                mergedNcSet = thisNcSet.union(otherNcSet)
                mergedSpace[nc] = mergedNcSet
            else:
                # in this space but not the other
                mergedSpace[nc] = self.internalSpace[nc]
                
        # find in the other space but not in this one
        for nc in otherSpace.keys():
            if nc not in self.internalSpace.keys():
                mergedSpace[nc] = otherSpace[nc]
        
        # union pstrats
        unionPstrats = self.pstrats.union(clusterGenerationSpec.pstrats)
        
        return SimpleClusterGenerationSpecification(self.hwSpecs, mergedSpace, unionPstrats)
    
    def __buildInternalSpace__(self):
        self.internalSpace = {}
        
        # all possible ncs given hardware
        allPhysicalCores = self.hwSpecs['coresInCluster']
        for nc in list(range(1, allPhysicalCores + 1)):
            
            # given this nc, find possible cpv/idf using SimpleRules
            cpvs = self.simpleRules.allCpvGivenNc(nc)
            ncSet = self.__buildSetWithCpvs__(nc, cpvs)
                        
            # some ncs will be empty, don't add them
            if len(ncSet) > 0:
                self.internalSpace[nc] = ncSet
                            
    def __constrainWithNc__(self, ncTuple):
        # only keep the requested ncs in the updated cluster space
        # requested ncs that are not in the current space are ignored
        constrainedSpace = {}
        for nc in ncTuple:
            if nc in self.internalSpace.keys():
                constrainedSpace[nc] = self.internalSpace[nc]
                
        return constrainedSpace
    
    def __constrainWithCpv__(self, cpvTuple):
        # only keep the requested cpvs in the updated cluster space
        # requested cpvs that are not in the current space are ignored
        constrainedSpace = {}
        
        # check for nc values that can be used with the provided cpvs
        # other nc values will not be further considered  
        for nc in self.internalSpace.keys():
            ncInSpace = False
            for cpv in cpvTuple:
                if nc in self.simpleRules.allNcGivenCpv(cpv):
                    ncInSpace = True # nc is in return space, take it into consideration
                    break
            
            if ncInSpace:
                # this nc is admitted, work it further
                # only have the tuples that include one of the cpvs
                thisConstraintNcSet = self.__buildSetWithCpvs__(nc, cpvTuple)
                
                # current space may be already constrained, merge current ncSet with new
                currentNcSet = self.internalSpace[nc]
                updatedNcSet = currentNcSet.intersection(thisConstraintNcSet)
                constrainedSpace[nc] = updatedNcSet
                
        return constrainedSpace
    
    def __constrainWithIdf__(self, idfTuple):
        # only keep the requested idfs in the updated cluster space
        # requested idfs that are not in the current space are ignored
        constrainedSpace = {}
        
        # check for nc values that can be used with the provided idfs
        # other nc values will not be further considered  
        for nc in self.internalSpace.keys():
            ncInSpace = False
            for idf in idfTuple:
                if nc in self.simpleRules.allNcGivenIdf(idf):
                    ncInSpace = True # nc is in return space, take it into consideration
                    break
            
            if ncInSpace:
                # this nc is admitted, work it further
                # only have the tuples that include one of the idfs
                thisConstraintNcSet = self.__buildSetWithIdfs__(nc, idfTuple)
                
                # current space may be already constrained, merge current ncSet with new
                currentNcSet = self.internalSpace[nc]
                updatedNcSet = currentNcSet.intersection(thisConstraintNcSet)
                constrainedSpace[nc] = updatedNcSet
                
        return constrainedSpace
    
    def __constrainWithPhysicalMachines__(self, physicalMachinesTuple):
        '''Physical machines are given in a tuple. For each physicalMachines value, the
        virtual cluster should have exactly the amount of physical machines specified.
        The virtual clusters for each value are aggregated.
        '''  
        
        # explore every value in the space, use the simple specification to unit
        # if the virtual cluster can be deployed in any of the values specified
        constrainedSpace = {}
        for nc in self.internalSpace.keys():
             
            currentNcSet = self.internalSpace[nc]
            constrainedNcSet = []
            for cpvIdfTuple in currentNcSet:
                idf = cpvIdfTuple[1]
                validCluster = self.simpleRules.canBeDeployedInAny(nc, idf, physicalMachinesTuple)
                if validCluster: 
                    constrainedNcSet.append(cpvIdfTuple)
                    
            if len(constrainedNcSet) > 0:
                # this nc has at least one virtual cluster that satisfies
                constrainedSpace[nc] = set(constrainedNcSet)
                
        return constrainedSpace
    
    def __buildSetWithCpvs__(self, nc, cpvs):
        ncSet = set([])
        for cpv in cpvs:
            # for nc/cpv, find idf. cpv may not satisfy the nc/idf combination
            idfs = self.simpleRules.allIdfGiven(nc, cpv)
            for idf in idfs:
                if cpv in self.simpleRules.allCpvGiven(nc, idf):
                    # nc/cpv/idf is satisfied, add (cpv,idf) tuple to set
                    ncSet.add((cpv, idf))
        return ncSet
    
    def __buildSetWithIdfs__(self, nc, idfs):
        ncSet = set([])
        for idf in idfs:
            # for nc/idf, find possible cpvs. cpv may not satisfy the nc/idf combination
            cpvs = self.simpleRules.allCpvGiven(nc, idf)
            for cpv in cpvs:
                if idf in self.simpleRules.allIdfGiven(nc, cpv):
                    # nc/cpv/idf is satisfied, add (cpv,idf) tuple to set
                    ncSet.add((cpv, idf))
        return ncSet