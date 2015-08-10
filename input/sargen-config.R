#########
# Parameters for configuring sar-analyzer.R
#########

# must contain 'usr' and 'sys'!
input.cpu.headers = c('usr', 'sys', 'iowait', 'irq', 'guest', 'idle')

# file inside config with scalar metrics
input.metrics.config = 'metrics-app.csv'

# prefix for vm/host
prefix.vm = 'V'
prefix.host = 'H'

# prefix for parameters (code assumes length 4!)
tag.cpu.user = 'usrC'
tag.cpu.system = 'sysC'

tag.memory.free = 'memF'
tag.memory.used = 'memU'

tag.network.received = 'netR'
tag.network.transmitted = 'netT'

#######
# Should not alter utility functions
#######

# System and user time (default)
getCpuHeaders <- function(coreIndex, is.vm) {
	prefix = getMachinePrefix(is.vm)
	coreTag = formatC(coreIndex, width = 3, format = "d", flag = "0") 
	c(paste(prefix, tag.cpu.user, coreTag, sep=''), paste(prefix, tag.cpu.system, coreTag, sep=''))
}

# Free and Used memor (kilobytes)
getMemoryHeaders <- function(nodeIndex, is.vm) {
  
  #c(paste('kmf', nodeTag, sep=''), paste('kmu', nodeTag, sep=''))
  prefix = getMachinePrefix(is.vm)
  nodeTag = getNodeTag(nodeIndex)
  c(paste(prefix, tag.memory.free, nodeTag, sep=''), paste(prefix, tag.memory.used, nodeTag, sep=''))
}

# Received and Transmitted bytes through network (kb/s)
getNetworkHeaders <- function(nodeIndex, is.vm) {
  #c(paste('nrk', nodeTag, sep=''), paste('ntk', nodeTag, sep=''))

  prefix = getMachinePrefix(is.vm)
  nodeTag = getNodeTag(nodeIndex)
  c(paste(prefix, tag.network.received, nodeTag, sep=''), paste(prefix, tag.network.transmitted, nodeTag, sep=''))
}

getCpuFilename <- function(nodeName) {
  paste('metrics', nodeName, 'cpu.txt', sep='-')
}

getMemoryFilename <- function(nodeName) {
  paste('metrics', nodeName, 'memory.txt', sep='-') 
}

getNetworkFilename <- function(nodeName) {
  paste('metrics', nodeName, 'network.txt', sep='-') 
}

getNodeTag <- function(nodeIndex) {
	nodeTag = formatC(nodeIndex, width = 3, format = "d", flag = "0") 
}

getMachinePrefix <- function(is.vm) {
	if (is.vm) {
		prefix = prefix.vm
	} else {
		prefix = prefix.host
	}
	prefix
}
