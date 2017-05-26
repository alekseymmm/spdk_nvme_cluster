# spdk_nvme_cluster
Set of scripts to deploy NVME-cluster using spdk for NVMEoF targets. I use it to deploy cluster with 2NVME drives in each node and 2 Inifiniband ports for interconnect.

Required software
1. Linux kernel 4.9. Tested on 4.9.22 but could work with  other versions.
2. Mellanox OFED Drivers. I used MLNX_OFED_LINUX-4.0-2.0.0.1-rhel7.2-x86_64
3. Intel SPDK. https://github.com/spdk/spdk

How to use
1. Build your Linux kernel with NVME Support. https://community.mellanox.com/docs/DOC-2508 
2. Configure IPoIB using Mellanox drivers.
3. Install SPDK to defalt location or specify it in scripts.
4. Do steps 1-3 for all nodes in your cluster.
5. Provide ssh access without password from managing node (It is not required to be one of your cluster node) because scripts use sshpass to deploy
6. Write info about your nodes (ip and ib addreses) in the config
7. Chose whether you wih to deploy it as md raid volumes or as zfs volumes. MD faster but zfs provides a lot of functionality, like dedup, compression, snapshots, thin provisioning and so on.
8. Run main script

