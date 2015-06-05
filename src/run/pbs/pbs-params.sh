########################################################
# Deployment parameters for applications based on PBS  #
########################################################

# Normal
PBS_MASTER='master.pbs'

# MPI Analyzer
#PBS_MASTER='analyzer.pbs'

# Some parameters
PBS_WALLTIME="2:00:00"
PBS_MEMORY="1024" # unused

PBS_SERVER='/var/spool/torque/server_priv'
