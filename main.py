
from subprocess import call, Popen
from spdk_conf import create_nvmf_config

NVME_SIZE = 1600 # GB

class Node:
    def __init__(self, name, ip_addr, ib_addr1, ib_addr2):
        self.name = name
        self.ip_addr = ip_addr
        self.ib_addr1 = ib_addr1
        self.ib_addr2 = ib_addr2

def reset_nvme(node_ip_addr, dev):
    #reset nvme to default
    cmd = "sshpass ssh root@" + \
        node_ip_addr +" 'yes | hdm reset-to-defaults --path " + dev + "'"

    print(cmd)
    call(cmd, shell=True)

def reset_all_nodes_nvme(nodes):
    for name, node in nodes.items():
        print("Reseting all NVME on node: " + name + " ...")
        reset_nvme(node.ip_addr, "/dev/nvme0")
        reset_nvme(node.ip_addr, "/dev/nvme1")
        print("Reset done")


def delete_namespaces(node_ip_addr, dev):
    #after reset there is only one namespace
    cmd = "sshpass ssh root@" + \
        node_ip_addr +" 'yes | hdm manage-namespaces --delete --id 1 --path " +\
        dev + "'"

    print(cmd)
    call(cmd, shell=True)

def delete_all_nodes_namespaces(nodes):
    for name, node in nodes.items():
        print("Delete all NVME namespaces on node: " + name + " ...")
        delete_namespaces(node.ip_addr, "/dev/nvme0")
        delete_namespaces(node.ip_addr, "/dev/nvme1")
        print("Delete done")

def load_conf(filename):
    nodes = {}
    with open(filename, "r") as f:
        for line in f:
            #remove line break
            line = line.replace("\n", "")

            [name, ip_addr, ib_addr1, ib_addr2] = line.split(" ")
            new_node = Node(name, ip_addr, ib_addr1, ib_addr2)
            nodes[name] = new_node

    return nodes

def create_namespaces(node_ip_addr, ns_size, ns_count):
    count1 = (ns_count + 1) / 2 #number of ns on the first nvme
    count2 = ns_count - count1

    for i in range(1, count1 + 1):
        cmd = "sshpass ssh root@" + \
              node_ip_addr + " 'yes | hdm manage-namespaces --create --id " +\
              str(i) + " --size " + str(ns_size) + " --path /dev/nvme0'"

        print(cmd)
        call(cmd, shell=True)

    for i in range(1, count2 + 1):
        cmd = "sshpass ssh root@" + \
              node_ip_addr + " 'yes | hdm manage-namespaces --create --id " +\
              str(i) + " --size " + str(ns_size) + " --path /dev/nvme1'"

        print(cmd)
        call(cmd, shell=True)

def create_all_nodes_namespaces(nodes):
    num_nodes = len(nodes)
    num_nodes = 3
    ns_size = NVME_SIZE / ((num_nodes + 1) / 2)

    for name, node in nodes.items():
        print("Create NVME namespaces on node: " + name + " ...")
        create_namespaces(node.ip_addr,ns_size, num_nodes)
        print("Create namespaces done")

def create_nvmf_target(node):
    create_nvmf_config(node)
    cmd = "sshpass scp nvmf.rain.in root@" + \
          node.ip_addr + ":/root/spdk/etc/spdk/"

    print(cmd)
    call(cmd, shell=True)

    #modprobe nvme-rdma
    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \'modprobe nvme-rdma\'"

    print(cmd)
    call(cmd, shell=True)

    #modprobe nvmet-rdma
    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \'modprobe nvmet-rdma\'"

    print(cmd)
    call(cmd, shell=True)

    #setup spdk nvme
    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \'/root/spdk/scripts/setup.sh\'"

    print(cmd)
    call(cmd, shell=True)

    #firstly kill all possible tgts
    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \'killall /root/spdk/app/nvmf_tgt/nvmf_tgt\'"

    print(cmd)
    call(cmd, shell=True)

    #run nvmf target
    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \'nohup /root/spdk/app/nvmf_tgt/nvmf_tgt -c /root/spdk/etc/spdk/nvmf.rain.in > /dev/null 2> /dev/null < /dev/null &\'"

    print(cmd)
    call(cmd, shell=True)


def reset_spdk(nodes):
    #rescan using spdk
    for name, node in nodes.items():
        cmd = "sshpass ssh root@" + node.ip_addr + \
              " \'/root/spdk/scripts/setup.sh reset\'"

        print(cmd)
        call(cmd, shell=True)

        cmd = "sshpass ssh root@" + \
              node.ip_addr + " 'hdm scan'"

        print(cmd)
        call(cmd, shell=True)

def main():
    nodes = load_conf("nodes.conf")
    reset_spdk(nodes)
    #reset_all_nodes_nvme(nodes)
    #delete_all_nodes_namespaces(nodes)
    #create_all_nodes_namespaces(nodes)
    create_nvmf_target(nodes["raidix1"])


    return 0

if __name__ == "__main__":
    #run main script
    main()
    print("done.")
