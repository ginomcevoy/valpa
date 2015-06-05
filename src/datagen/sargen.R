#!/usr/bin/env r
#
# Reads pbsnodes.txt from a directory, identifies VMs and hosts
 
# Validate input 
if (is.null(argv) | length(argv)<2) {
 
  cat("Usage: sargen.r configDir cpv phycores execCount {execNames...} {appTimes...} configOutputDir \n")
  q()
}

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
  cpuUser = data.splitWindow[which(substr(names(data.splitWindow), 1, 4) == 'usrC')]
  cpuSystem = data.splitWindow[which(substr(names(data.splitWindow), 1, 4) == 'sysC')]
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
  result
}

# read pbsnodes.txt   
configDir = argv[1]
nodeNames = read.table(paste(configDir,'pbsnodes.txt', sep='/'), col.names=c('names'))

# separate vms and hosts
vms = nodeNames[which(substr(nodeNames$names, 1, 3) == 'kvm'),]
vms = sort(vms)
hosts = nodeNames[which(nodeNames$names != vms),]
hosts = sort(hosts)

# config info
cpv = as.numeric(argv[2])
phycores = as.numeric(argv[3])
execCount = as.numeric(argv[4])

# get execDirs
execNames = argv[5:(4 + execCount)]
execDirs = paste(configDir, execNames, sep='/')

# get appTimes
appTimes = as.numeric(argv[(5 + execCount):(4 + 2*execCount)])

configOutputDir = argv[length(argv)]

# Work each execution independently
execIndex = 1
for (execDir in execDirs) {

  # prepare for an execution
  vmIndex = 1
  coreIndex = 1
  hostIndex = 1

  # Format execIndex
  execTag = formatC(execIndex, width = 3, format = "d", flag = "0") 

  # data from each VM and host is stored in a list,
  # as it may be of different sizes
  output.list = list()

  ###
  # VM DATA
  ###
  for (vm in vms) {

    # Data from 1 VM goes here
    vm.frame = NULL

    # Format vm index
    vmTag = formatC(vmIndex, width = 3, format = "d", flag = "0") 

    ###
    # VM MEMORY
    ###

    # Open metrics-$vm-memory.txt 
    colNames = c(paste('kmfV', vmTag, sep=''), paste('kmuV', vmTag, sep=''))
    memoryFile = paste('metrics', vm, 'memory.txt', sep='-') 
    memory.data = read.table(paste(execDir, memoryFile, sep='/'), col.names=(colNames))

    # Add data from this VM to output
    vm.frame = memory.data

    ###
    # VM NETWORK
    ###

    # Open metrics-$vm-network.txt 
    colNames = c(paste('nrkV', vmTag, sep=''), paste('ntkV', vmTag, sep=''))
    networkFile = paste('metrics', vm, 'network.txt', sep='-')
    network.data = read.table(paste(execDir, networkFile, sep='/'), col.names=(colNames))

    # Add data from this VM to output
    vm.frame = cbind(vm.frame, network.data)

    ###
    # VM CPU
    ###

    # Open metrics-$vm-cpu.txt 
    # data headers
    colNames = c('user', 'nice', 'system', 'iowait', 'steal', 'idle')
    cpuFile = paste('metrics', vm, 'cpu.txt', sep='-')
    cpu.data = read.table(paste(execDir, cpuFile, sep='/'), col.names=(colNames))
    cpu.data = cpu.data[c('user','system')]

    # Select rows for each CPU
    for (i in 0:(cpv-1)) {

      # Format core index
      coreTag = formatC(coreIndex, width = 3, format = "d", flag = "0") 
    
      # This gets all rows for cpui (cpu0, cpu1,...)
      row.data = cpu.data[seq(i+1, nrow(cpu.data), by=cpv),]

      # Names will be usrC001, usrC002, ... and sysC001, sysC002, ...
      cpu.usr.name = paste('usrC', coreTag, sep='')
      cpu.sys.name = paste('sysC', coreTag, sep='')
    
      # Append both cpuX entries to result
      cpu.2col.frame = data.frame(cpu=row.data)
      names(cpu.2col.frame) = c(cpu.usr.name, cpu.sys.name)
      vm.frame = cbind(vm.frame, cpu.2col.frame)

      # next virtual core (global for all VMs in exec)
      coreIndex = coreIndex + 1
    }

    # # Add data from this VM to output
    # vm.frame = cbind(vm.frame, network.data)

    # Add data from this VM to general output
    output.list[[vm]] = vm.frame


    vmIndex = vmIndex + 1
  }

  ###
  # HOST DATA
  ###
  for (host in hosts) {

    # Data from 1 host goes here
    host.frame = NULL

    # Format host index
    coreIndex = 1
    hostTag = formatC(hostIndex, width = 3, format = "d", flag = "0") 

    ###
    # HOST NETWORK
    ###

    # Open metrics-$host-network.txt 
    colNames = c(paste('nrkH', hostTag, sep=''), paste('ntkH', hostTag, sep=''))
    networkFile = paste('metrics', host, 'network.txt', sep='-')
    network.data = read.table(paste(execDir, networkFile, sep='/'), col.names=(colNames))

    # Add data from this host to output
    host.frame = network.data

    ###
    # HOST CPU (needed for the window cut)
    ###

    # Open metrics-$host-cpu.txt 
    # data headers
    colNames = c('user', 'nice', 'system', 'iowait', 'steal', 'idle')
    cpuFile = paste('metrics', host, 'cpu.txt', sep='-')
    cpu.data = read.table(paste(execDir, cpuFile, sep='/'), col.names=(colNames))
    cpu.data = cpu.data[c('user','system')]

    # Select rows for each CPU
    for (i in 0:(phycores-1)) {

      # Format core index
      coreTag = formatC(coreIndex, width = 3, format = "d", flag = "0") 
    
      # This gets all rows for cpui (cpu0, cpu1,...)
      row.data = cpu.data[seq(i+1, nrow(cpu.data), by=phycores),]

      # Names will be usrC001, usrC002, ... and sysC001, sysC002, ...
      cpu.usr.name = paste('usrC', coreTag, sep='')
      cpu.sys.name = paste('sysC', coreTag, sep='')
    
      # Append both cpuX entries to result
      cpu.2col.frame = data.frame(cpu=row.data)
      names(cpu.2col.frame) = c(cpu.usr.name, cpu.sys.name)
      host.frame = cbind(host.frame, cpu.2col.frame)

      # next virtual core (global for all VMs in exec)
      coreIndex = coreIndex + 1

    }

    # Add data from this host to general output
    output.list[[host]] = host.frame
    
    hostIndex = hostIndex + 1
  }

  ###
  # MAKING OUTPUT THE SAME LENGTH (appTime)
  ###
  #str(output.list)

  # Loop for VMs and hosts
  for (node in nodeNames$names) {

    # get data for this node
    node.frame = output.list[[node]]

    # window = number of samples * freq (1) - [| appTime |]
    appTimeCeil = ceiling(appTimes[execIndex])
    windowSize = dim(node.frame)[1] - appTimeCeil

    # use the window split to cut and stay with most CPU activity
    output.list[[node]] = cutMostIdleData(node.frame, windowSize)
  }

  #str(output.list)

  ####
  # SORTING OUTPUT
  ####

  # Temporary frames for VMs
  freeMem = NULL
  usedMem = NULL
  networkReceive = NULL
  networkTransmit = NULL
  cpuUser = NULL
  cpuSystem = NULL

  for (vm in vms) {
    vm.frame = output.list[[vm]] 
  
    # Get all free memory (kmfV)
    freeMem.thisvm = vm.frame[which(substr(names(vm.frame), 1, 4) == 'kmfV')]
    if (is.null(freeMem)) {
      freeMem = freeMem.thisvm
    } else {
      freeMem = cbind(freeMem, freeMem.thisvm)
    } 

    # Get all used memory (kmuV)
    usedMem.thisvm = vm.frame[which(substr(names(vm.frame), 1, 4) == 'kmuV')]
    if (is.null(usedMem)) {
      usedMem = usedMem.thisvm
    } else {
      usedMem = cbind(usedMem, usedMem.thisvm)
    } 

    #Get all network receive (nrkV)
    networkReceive.thisvm = vm.frame[which(substr(names(vm.frame), 1, 4) == 'nrkV')]
    if (is.null(networkReceive)) {
      networkReceive = networkReceive.thisvm
    } else {
      networkReceive = cbind(networkReceive, networkReceive.thisvm)
    }

    #Get all network transmit (ntkV)
    networkTransmit.thisvm = vm.frame[which(substr(names(vm.frame), 1, 4) == 'ntkV')]
    if (is.null(networkTransmit)) {
      networkTransmit = networkTransmit.thisvm
    } else {
      networkTransmit = cbind(networkTransmit, networkTransmit.thisvm)
    }

    # Get all CPU user (usrC)
    cpuUser.thisvm = vm.frame[which(substr(names(vm.frame), 1, 4) == 'usrC')]
    if (is.null(cpuUser)) {
      cpuUser = cpuUser.thisvm
    } else {
      cpuUser = cbind(cpuUser, cpuUser.thisvm)
    }

    # Get all CPU system (sysC)
    cpuSystem.thisvm = vm.frame[which(substr(names(vm.frame), 1, 4) == 'sysC')]
    if (is.null(cpuSystem)) {
      cpuSystem = cpuSystem.thisvm
    } else {
      cpuSystem = cbind(cpuSystem, cpuSystem.thisvm)
    }

  } 

  # Temporary frames for hosts
  networkReceive.hosts = NULL
  networkTransmit.hosts = NULL

  for (host in hosts) {
    host.frame = output.list[[host]]

    #Get all network receive (nrkH)
    networkReceive.thishost = host.frame[which(substr(names(host.frame), 1, 4) == 'nrkH')]
    if (is.null(networkReceive.hosts)) {
      networkReceive.hosts = networkReceive.thishost
    } else {
      networkReceive.hosts = cbind(networkReceive.hosts, networkReceive.thishost)
    }

    #Get all network transmit (ntkV)
    networkTransmit.thishost = host.frame[which(substr(names(host.frame), 1, 4) == 'ntkH')]
    if (is.null(networkTransmit.hosts)) {
      networkTransmit.hosts = networkTransmit.thishost
    } else {
      networkTransmit.hosts = cbind(networkTransmit.hosts, networkTransmit.thishost)
    }
  }
  
  # C + C + V + V + V + V + H + H
  final.frame = cbind(cpuUser, cpuSystem, freeMem, usedMem, networkReceive, networkTransmit, networkReceive.hosts, networkTransmit.hosts)
  #str(final.frame)

  # write outputs to config/exec001, config/exec002,...
  execFilename = paste('exc', execTag, '.csv', sep='')
  outputFile = paste(configOutputDir, execFilename, sep='/')
  write.table(final.frame, file=outputFile, sep=';', row.names=FALSE, col.names=FALSE)

  execIndex = execIndex + 1
}

# Create the header array
# C + C + V + V + V + V + H + H
makeHeader <- function(data) {

  # CPU user time
  usrHeader = names(data[which(substr(names(data), 1, 4) == 'usrC')])
  header = usrHeader

  # CPU system time
  sysHeader = names(data[which(substr(names(data), 1, 4) == 'sysC')])
  header = c(header, sysHeader)

  # free memory
  freeMemHeader =  names(data[which(substr(names(data), 1, 4) == 'kmfV')])
  header = c(header, freeMemHeader)

  # used memory
  usedMemory =  names(data[which(substr(names(data), 1, 4) == 'kmuV')])
  header = c(header, usedMemory)

  # network receive
  networkReceiveHeader =  names(data[which(substr(names(data), 1, 4) == 'nrkV')])
  header = c(header, networkReceiveHeader)

  # network send
  networkSendHeader =  names(data[which(substr(names(data), 1, 4) == 'ntkV')])
  header = c(header, networkSendHeader)

  # network receive host
  networkReceiveHostHeader =  names(data[which(substr(names(data), 1, 4) == 'nrkH')])
  header = c(header, networkReceiveHostHeader)

  # network send host
  networkSendHostHeader =  names(data[which(substr(names(data), 1, 4) == 'ntkH')])
  header = c(header, networkSendHostHeader)

  header
}

# Save header to file
writeHeader <- function(header, configOutputDir, filename='header.txt') {
  outputFile = paste(configOutputDir, filename, sep='/')
  cat(header, file=outputFile, sep=' ')
}

# Use data from last execution 
header = makeHeader(final.frame)
writeHeader(header, configOutputDir)