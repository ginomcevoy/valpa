class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

CpuTopoOpt = Enum(["DEFAULT", "CORRECT", "ONE_CORE", "ONE_PROC"])
DiskOpt = Enum(["ide", "scsi", "virtio"])
NetworkOpt = Enum(["virtio", "vhost", "sr-iov"])
PinningOpt = Enum(["BAL_ONE", "BAL_SET", "GREEDY", "SPLIT", "NONE"])

# From the OpenMPI 1.8.4 mpirun man page:
# --bind-to <foo> 
# Bind processes to the specified object, defaults to core. 
# Supported options include slot, hwthread, core, l1cache, 
# l2cache, l3cache, socket, numa, board, and none.
MPIBindOpt = Enum(["slot", "hwthread", "core", "l1cache", "l2cache", "l3cache",
                   "socket", "numa", "board", "none"])
