################################################
# Global parameters for running experiments
################################################

# Verbosity
VERBOSE=0

# Output dir for execution configuration
EXEC_CONFIG_DIR='/tmp/execs'

# Format for time.sh
TIME_FORMAT='%C\nUser\tSystem\tEllapsed\n%U\t%S\t%e'

# Collective output for times (for each execution config)
TIME_OUTPUT="times.txt"

# Time to wait for VMs to load 
DEPLOY_TIME=1

# Supported PBS applications - will look here to see if PBS scripts will be used
PBS_APPS='parpac,none'

# Date format used to stamp output files
DATE_FORMAT='%Y-%m-%d-%H:%M'

# Fix for Ubuntu Lucid (libvirt 0.7.5 < 0.9.0), need to call vcpupin as VMs go online
# Values: true / false
REQUIRES_VCPUPIN='true'

# Fix for NFS, VMs don't mount shared dir automatically
# Values: true / false
USE_NFS='false'
