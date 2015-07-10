# Vespa (Virtualized Experiments for Scientific Parallel Applications)

 Vespa is designed to support the definition and production of controlled application executions running on virtual machines (VMs), as well as gathering performance metrics related to these executions. The main goal of Vespa is to manage the systematic experimentation of applications deployed on different virtual clusters, while supporting rich definitions for the cluster topology and mappings to underlying physical resources. The results will later translate into a knowledge repository with real (non-simulated) data for studying the effects of virtual cluster features on different scientific applications.

 ## Dependencies

Since Vespa is meant to be deployed on a physical cluster and support virtual clusters, there are different sets of dependencies:

### Common requirements
- Python 2.7.x
- Libvirt 1.x+ (libvirt-bin package)
- OpenSSH Server (openssh-server package) with password-less login between physical nodes and VMs 

### Requirements for head node
- Ansible 1.9+ (ansible package)
- Jinja 2 (included as dependency with Ansible)
- GNU parallel (parallel package)
- Torque server and Torque client (torque-server torque-client packages)
- NFS or equivalent for shared files in the physical cluster

### Requirements for computing nodes
- KVM
- Torque Node Manager (torque-mom package)
- Sysstat monitoring (sysstat package)
