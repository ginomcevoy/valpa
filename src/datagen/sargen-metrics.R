#!/usr/bin/env r
########
# Analyzes SAR metrics (pre-processed into monitor*.txt by the monitor package)
# Works on a single config dir, generates n CSV, one for each execution 
# (exc001.csv, exc002.csv, ...) in output dir. Also generates header.txt for that config.
########

##########
# Entities:  objects with monitored metrics
##########
MonitoredMetrics <- function(metrics, nodeName) {
  if (!is.data.frame(metrics)) {
    stop("Invalid MonitoredMetrics construction")
  }
  obj = list("frame" = metrics, "nodeName" = nodeName)
  class(obj) = "MonitoredMetrics"
  obj
}

# execDir = full path to execution dir
# nodeName = vm / host name
# coreCount = cpv (for VM) or cpm (for host)
# coreIndex = the first core number for the node
CpuMetrics <- function(execDir, nodeName, coreCount, coreIndex, is.vm) {
  
  # Read from preferences
  colNames = input.cpu.headers 
  header = c('usr','sys')
  cpuFile = getCpuFilename(nodeName) # e.g. "metrics-kvm-pbs083-01-cpu.txt" 
  
  # open data file
  cpu.data = read.table(paste(execDir, cpuFile, sep='/'), col.names=(colNames), header=TRUE)
  cpu.data = cpu.data[header]
  
  node.frame = NULL
  
  # Select rows for each CPU
  for (i in 0:(coreCount-1)) {
    
    # Format core index
    cpu.headers = getCpuHeaders(coreIndex, is.vm)
    
    # This gets all rows for cpui (cpu0, cpu1,...)
    row.data = cpu.data[seq(i+1, nrow(cpu.data), by=coreCount),]
    
    # Names will be VusrC001, VusrC002, ... and VsysC001, VsysC002, ...
    cpu.usr.name = cpu.headers[1]
    cpu.sys.name = cpu.headers[2]
    
    # Append both cpuX entries to result
    cpu.2col.frame = data.frame(cpu=row.data)
    names(cpu.2col.frame) = c(cpu.usr.name, cpu.sys.name)
    if (is.null(node.frame)) {
      node.frame = cpu.2col.frame
    } else {
      node.frame = cbind(node.frame, cpu.2col.frame)
    }
    
    # next core
    coreIndex = coreIndex + 1
  }
  
  # Output
  row.names(node.frame) = NULL
  cpuMetrics = MonitoredMetrics(node.frame, nodeName)
}

# execDir = full path to execution dir
# nodeName = vm / host name
# nodeTag = node identifier, e.g. V002 (2nd VM) or H003 (third host)
MemoryMetrics <- function(execDir, nodeName, nodeIndex, is.vm) {
  
  # Read from preferences
  header = getMemoryHeaders(nodeIndex, is.vm)
  memoryFile = getMemoryFilename(nodeName) # e.g. "metrics-kvm-pbs083-01-memory.txt"
  
  memory.data = read.table(paste(execDir, memoryFile, sep='/'), col.names=(header), header=TRUE)
  
  # Output
  memMetrics = MonitoredMetrics(memory.data, nodeName)
}

# execDir = full path to execution dir
# nodeName = vm / host name
# nodeTag = node identifier, e.g. V002 (2nd VM) or H003 (third host)
NetworkMetrics <- function(execDir, nodeName, nodeIndex, is.vm) {
  
  # Read from preferences
  header = getNetworkHeaders(nodeIndex, is.vm)
  networkFile = getNetworkFilename(nodeName) # e.g. "metrics-kvm-pbs083-01-network.txt"
  
  network.data = read.table(paste(execDir, networkFile, sep='/'), col.names=(header), header=TRUE)
  
  # Output
  networkMetrics = MonitoredMetrics(network.data, nodeName)
}

# Aggregates metrics for a node, or for all nodes in a MonitoredMetrics object.
# First case, assumes that all entries have same nodeName, and first nodeName is used for output
# Second case, only puts first nodeName and should be ignored
AggregatedMetrics <- function(listOfMonitoredMetrics, execDir) {
  
  if (!is.list(listOfMonitoredMetrics)) {
    stop("need list of MonitoredMetrics")
  }
  
  size = -1
    
  aggregated.frame = NULL
  nodeName = NULL
  
  lapply(listOfMonitoredMetrics, function(monitoredMetric) {
    if (class(monitoredMetric) != 'MonitoredMetrics') {
      stop("need list of MonitoredMetrics 2")
    }
    
    if (size == -1) {
      size <<- dim(monitoredMetric$frame)[1]
    }
    
    # Policy: each MonitorMetrics frame should be same length
    if (size != dim(monitoredMetric$frame)[1]) {
      print(monitoredMetric)
      msg = paste("Failed size invariant at", execDir, "for node", monitoredMetric$nodeName)
      stop(msg)
    }
    
    # build the aggregate
    if (is.null(aggregated.frame)) {
      aggregated.frame <<- monitoredMetric$frame
      nodeName <<- monitoredMetric$nodeName
    } else {
      aggregated.frame <<- cbind(aggregated.frame, monitoredMetric$frame)
    }
  })

  # Output
  aggregatedMetrics = MonitoredMetrics(aggregated.frame, nodeName)
}

######
# Data finders: find the sources to later build the entities
######

# Finds cpv value for a config, reading topology.txt
findCpv <- function(configDir) {
  topologyFile = paste(configDir, '/../topology.txt', sep='')
  source(topologyFile) # will read variables
  cpv = C/V
}

# Finds all execution dirs within a configDir (subdirectories)
# Returns the full paths
findExecutionDirs <- function(configDir) {
  #configAndExecs = list.dirs(configDir) # also adds configDir
  #configAndExecs[-1] # removed
  list.dirs(configDir)
}

# Loads the metrics-config.csv and selects the appTimes.
findAppTimes <- function(configDir) {
  filename = paste(configDir, input.metrics.config, sep='/')
  config.metrics = read.table(filename, sep=';', header=TRUE)
  config.metrics[,'appTime']
}

findVmsAndHosts <- function(configDir) {
  
  # read pbsnodes.txt   
  nodeNames = read.table(paste(configDir,'pbsnodes.txt', sep='/'), col.names=c('names'), stringsAsFactors=FALSE)
  
  # separate vms and hosts
  vms = nodeNames[which(substr(nodeNames$names, 1, 3) == 'kvm'),]
  vms = sort(vms)
  hosts = setdiff(nodeNames$names, vms)
  hosts = sort(hosts)
  list('vms' = vms, 'hosts' = hosts, 'all' = c(vms, hosts))
}

#####
# Logic for making data from different nodes the same size
#####

# Selects two sub-windows from the data, one part at the top and another at the bottom
splitWindow <- function(data, rowCount, offset, windowSize) {
  data.top = data[1:(windowSize-offset),]
  data.bottom = data[(rowCount-offset+1): (rowCount),]
  if (offset == windowSize) {
    result = data.bottom
  } else if (offset == 0) {
    result = data.top
  } else {
    result = rbind(data.top, data.bottom)
  }
  
  result
}

# Calculates a specific metric for the window (CPU user + CPU system of all entries)
windowMetric <- function(data.splitWindow) {
  # Get CPU user, CPU system
  cpuUser = data.splitWindow[which(substr(names(data.splitWindow), 2, 5) == tag.cpu.user)]
  cpuSystem = data.splitWindow[which(substr(names(data.splitWindow), 2, 5) == tag.cpu.system)]
  metric = sum(cpuUser) + sum(cpuSystem)
}

mostIdle <- function(data, rowCount, windowSize) {
  mostIdle = Inf
  bestOffset = -1
  for (offset in seq(0, windowSize)) {
    # find a split window and evaluate its metric (CPU time)
    data.splitWindow = splitWindow(data, rowCount, offset, windowSize)
    metric = windowMetric(data.splitWindow)
    if (metric < mostIdle) {
      mostIdle = metric
      bestOffset = offset
    }
  }
  bestOffset
}

cutMostIdleData <- function(data, windowSize) {
  # trivial case: nothing to do
  if (windowSize == 0) {
    result = data
    
  } else {
    # find the best offset to cut data
    rowCount = dim(data)[1]
    bestOffset = mostIdle(data, rowCount, windowSize)
    
    # Select data outside the split window
    if (bestOffset == 0) {
      result = data[(windowSize + 1) : rowCount,]
    } else if (bestOffset == windowSize) {
      result = data[1:(rowCount - windowSize),]
    } else {
      result = data[(bestOffset + 1) : (rowCount - windowSize + bestOffset),]
    }
  }
  row.names(result) = NULL
  result
}

######
# Coordinators: Iterate the executions/nodes to build entities
######

# Finds CpuMetrics, MemoryMetrics, NetworkMetrics for a single node in 
# a single exc and aggregates the metrics
# nodeIndex represents the index for either a VM or a Host (starts at 1)
# coreCount is either cpv or cpm
calculateMetricsForNode <- function(execDir, nodeName, coreCount, nodeIndex, is.vm) {
  
  # coreIndex also starts at 1
  coreIndex = (nodeIndex - 1) * coreCount + 1
  
  cpuMetrics = CpuMetrics(execDir, nodeName, coreCount, coreIndex, is.vm)
  memoryMetrics = MemoryMetrics(execDir, nodeName, nodeIndex, is.vm)
  networkMetrics = NetworkMetrics(execDir, nodeName, nodeIndex, is.vm)
  
  # when
  nodeMetrics = AggregatedMetrics(list(cpuMetrics, memoryMetrics, networkMetrics), execDir)
}

# Finds metrics for each VM and each host. Since the data can have different
# sizes, need to use a list
calculateMetricsForExecutionUneven <- function(execDir, nodeNames, cpv, phycores) {
  
  output.list = list()
  
  # Iterate all the VMs
  vmIndex = 1
  for (vm in nodeNames$vms) {
    output.list[[vm]] = calculateMetricsForNode(execDir, vm, cpv, vmIndex, TRUE)
    vmIndex = vmIndex + 1
  }
  
  # Iterate all the hosts
  hostIndex = 1
  for (host in nodeNames$hosts) {
    output.list[[host]] = calculateMetricsForNode(execDir, host, phycores, hostIndex, FALSE)
    hostIndex = hostIndex + 1
  }
  
  output.list
}

# Finds metrics for an execution, making it the same length
# appTime is for specific execution
calculateMetricsForExecutionEven <- function(execDir, nodeNames, cpv, phycores, appTime) {
  
  output.list = calculateMetricsForExecutionUneven(execDir, nodeNames, cpv, phycores)
  
  # Loop for VMs and hosts
  for (node in nodeNames$all) {
    
    # get data for this node
    node.frame = output.list[[node]]$frame
    
    # window = number of samples * freq (1) - [| appTime |]
    appTimeFloor = floor(appTime)
    node.frame.length = dim(node.frame)[1]
    windowSize =  node.frame.length - appTimeFloor
    
    if (windowSize < 0) {
      # Bugfix: sometimes monitoring data is incomplete 
      # (there are less monitored seconds than [|appTime|])
      # In this case, add missing lines as NaN, as many needed to complete [|appTime|]
      # Because of this, calculating metric means requires na.rm=TRUE
      for (row in seq(1, -windowSize)) {
        node.frame[(node.frame.length + row),] = rep(NaN, dim(node.frame)[2]) 
        output.list[[node]] = MonitoredMetrics(node.frame, node)
      }
    } else {
      # use the window split to cut excess and stay with most CPU activity
      node.frame.cut = cutMostIdleData(node.frame, windowSize)
      output.list[[node]] = MonitoredMetrics(node.frame.cut, node)
    }
    
  }
  
  output.list
}

# Sorts according to metric type
# evenMetrics is result from calculateMetricsForExecutionEven 
# this script assumes that all dataframes in evenMetrics have the same length
sortExecutionMetrics <- function(evenMetrics, nodeNames, execDir) {
  
  allMetrics.vms = sortByMachineType(evenMetrics, nodeNames, for.vms = TRUE)
  allMetrics.hosts = sortByMachineType(evenMetrics, nodeNames, for.vms = FALSE)
  allMetrics = c(allMetrics.vms, allMetrics.hosts)

  AggregatedMetrics(allMetrics, execDir)
}

# all.machines.type = names of either all vms or all hosts
# prefix.machine = either prefix.vm or prefix.host
sortByMachineType <- function(evenMetrics, nodeNames, for.vms) {

  if (for.vms) {
    all.machines.type = nodeNames$vms
    prefix.machine = prefix.vm
  } else {
    all.machines.type = nodeNames$hosts
    prefix.machine = prefix.host
  }

  # Temporary frames 
  freeMem = NULL
  usedMem = NULL
  networkReceive = NULL
  networkTransmit = NULL
  cpuUser = NULL
  cpuSystem = NULL

  for (machine in all.machines.type) {
    machine.frame = evenMetrics[[machine]]$frame
    
    # Get all free memory
    freeMem.id = paste(prefix.machine, tag.memory.free, sep='')
    freeMem.this = machine.frame[which(substr(names(machine.frame), 1, 5) == freeMem.id)]
    freeMem = addToPossiblyEmpty(freeMem, freeMem.this)
    
    # Get all used memory
    usedMem.id = paste(prefix.machine, tag.memory.used, sep='')
    usedMem.this = machine.frame[which(substr(names(machine.frame), 1, 5) == usedMem.id)]
    usedMem = addToPossiblyEmpty(usedMem, usedMem.this)
    
    #Get all network receive
    networkReceive.id = paste(prefix.machine, tag.network.received, sep='')
    networkReceive.this = machine.frame[which(substr(names(machine.frame), 1, 5) == networkReceive.id)]
    networkReceive = addToPossiblyEmpty(networkReceive, networkReceive.this)
    
    #Get all network transmit
    networkTransmit.id = paste(prefix.machine, tag.network.transmitted, sep='')
    networkTransmit.this = machine.frame[which(substr(names(machine.frame), 1, 5) == networkTransmit.id)]
    networkTransmit = addToPossiblyEmpty(networkTransmit, networkTransmit.this)
    
    # Get all CPU user
    cpuUser.id = paste(prefix.machine, tag.cpu.user, sep='')
    cpuUser.this = machine.frame[which(substr(names(machine.frame), 1, 5) == cpuUser.id)]
    cpuUser = addToPossiblyEmpty(cpuUser, cpuUser.this)
    
    # Get all CPU system
    cpuSystem.id = paste(prefix.machine, tag.cpu.system, sep='')
    cpuSystem.this = machine.frame[which(substr(names(machine.frame), 1, 5) == cpuSystem.id)]
    cpuSystem = addToPossiblyEmpty(cpuSystem, cpuSystem.this)
  } 

  # Use MonitoredMetrics objects
  cpuUser = MonitoredMetrics(cpuUser, 'all')
  cpuSystem = MonitoredMetrics(cpuSystem, 'all')
  freeMem = MonitoredMetrics(freeMem, 'all')
  usedMem = MonitoredMetrics(usedMem, 'all')
  networkReceive = MonitoredMetrics(networkReceive, 'all')
  networkTransmit = MonitoredMetrics(networkTransmit, 'all')
  
  allMetrics = list(cpuUser, cpuSystem, freeMem, usedMem, networkReceive, networkTransmit)
}

# Generate exc###.csv, header.txt
generateCsvOutputs <- function(sortedMetrics, execIndex, configOutputDir) {
  
  # Format execIndex
  execTag = formatC(execIndex, width = 3, format = "d", flag = "0") 
  
  # write outputs to config/exec001, config/exec002,...
  execFilename = paste('exc', execTag, '.csv', sep='')
  outputFile = paste(configOutputDir, execFilename, sep='/')
  write.table(sortedMetrics$frame, file=outputFile, sep=';', row.names=FALSE, col.names=FALSE)  
}

# Generate header.txt
generateHeaderOutput <- function(sortedMetrics, configOutputDir) {
  headerVector = colnames(sortedMetrics$frame)
  outputFile = paste(configOutputDir, 'header.txt', sep='/')
  cat(headerVector, file=outputFile, sep=' ')
  cat('\n', file=outputFile, sep='', append=TRUE)
}

# Coordinates the iteration of executions and calls functions for a single exec.
loopExecutions <- function(configDir, nodeNames, cpv, phycores, configOutputDir) {
  execDirs = findExecutionDirs(configDir) #full path
  appTimes = findAppTimes(configDir)
  
  execIndex = 1
  for (execDir in execDirs) {
    
    # get appTime
    appTime = appTimes[execIndex]
    
    # get metrics for execution and save
    evenMetrics = calculateMetricsForExecutionEven(execDir, nodeNames, cpv, phycores, appTime)
    sortedMetrics = sortExecutionMetrics(evenMetrics, nodeNames, execDir)
    generateCsvOutputs(sortedMetrics, execIndex, configOutputDir)
    
    # all went well, print execDir for log
    print(paste("OK:", execDir))
    
    execIndex = execIndex + 1
  }
  
  # write the header with the last sortedMetrics
  generateHeaderOutput(sortedMetrics, configOutputDir)
  
  # All went well
  print(paste("OK:", configDir))
}

#######
# Utility functions
######

addToPossiblyEmpty <- function(aggregation, toAdd) {
  if (is.null(aggregation)) {
      aggregation = toAdd
    } else {
      aggregation = cbind(aggregation, toAdd)
    }
    
}

list.dirs <- function(path=".",recursive=FALSE) {
  get.list <- list.files(path)
  if (length(get.list) == 0) {return(NULL)} #no files or directories
  get.list.fixed <- paste(path,get.list,sep="/")
  whichonesaredir <- file.info(get.list.fixed)$isdir
  if (!any(whichonesaredir)) {return(NULL)} #no directories, only files
  dirlist <- get.list.fixed[whichonesaredir]
  finaldirlist <- dirlist
  if ((recursive & length(dirlist) > 0)) {
    for (i in 1:length(dirlist)) {
      finaldirlist <- c(finaldirlist,list.dirs(dirlist[i],recursive))
    }
  }
  return(finaldirlist)
}

#######
# Main (
#######

# Main function, coordinates the major functions
generateExecutionMetrics <- function(configDir, phycores, configOutputDir) {
  
  # Gather arguments for loopExecutions
  cpv = findCpv(configDir)
  nodeNames = findVmsAndHosts(configDir)
  
  # make call
  loopExecutions(configDir, nodeNames, cpv, phycores, configOutputDir)
}

# Uncomment for testing
#argv = vector()
#argv[1] = '/home/giacomo2/vespa'
#argv[2] = '/home/giacomo2/experiments/arriving/parpac/nc4-cpv2-idf2-psNONE/e9b01aa4132532a40308d51c7ba99e6048cdcafd3a193af72d6619bdaa5d5980'
#argv[3] = '12'
#argv[4] = '/home/giacomo2/experiments/analyzed/parpac/cfg1'
 
# Read arguments from stdin
if (exists("argv")) {
  vespaDir = argv[1]
  configDir = argv[2]
  phycores = as.numeric(argv[3])
  configOutputDir = argv[4]

  # Load Preferences
  setwd(vespaDir)
  source("input/sargen-config.R")

  generateExecutionMetrics(configDir, phycores, configOutputDir)
}


