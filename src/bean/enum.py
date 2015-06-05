class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

CpuTopoOpt = Enum(["DEFAULT", "CORRECT", "ONE_CORE", "ONE_PROC"])
DiskOpt = Enum(["ide", "scsi", "virtio"])
NetworkOpt = Enum(["virtio", "vhost", "sr-iov"])
PinningOpt = Enum(["BAL_ONE", "BAL_SET", "GREEDY", "SPLIT", "NONE"])
MPIBindOpt = Enum(["BIND_CORE", "BIND_SOCKET", "NONE"])

if __name__ == '__main__':
    networkOpt = NetworkOpt.virtio
    print(networkOpt)