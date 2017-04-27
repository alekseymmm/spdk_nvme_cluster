
from subprocess import call, Popen, PIPE
from spdk_conf import create_nvmf_config
import time

import natsort

NVME_SIZE = 1500 # GB

class Node:
    def __init__(self, name, ip_addr, ib_addr1, ib_addr2):
        self.name = name
        self.ip_addr = ip_addr
        self.ib_addr1 = ib_addr1
        self.ib_addr2 = ib_addr2

def run_cmd(cmd_string, retry_on_failure_cnt):
    p = Popen(cmd_string, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    out_str = out.decode("utf-8")
    err_str = err.decode("utf-8")
    print(out_str)
    print(err_str)
    i = 1

    if (err_str != "" and retry_on_failure_cnt > 0):
        print("Try again cmd (" + cmd_string + ") retry_cnt: " + str(retry_on_failure_cnt))
        retry_on_failure_cnt -= 1
        time.sleep(2)
        i += 1
        run_cmd(cmd_string, retry_on_failure_cnt)

    if (err_str != "" and retry_on_failure_cnt == 0):
        print("Cmd (" + cmd_string + ") execution failed")


def reset_nvme(node_ip_addr, dev):
    cmd = "sshpass ssh root@" + \
          node_ip_addr + " 'hdm scan'"

    print(cmd)
    call(cmd, shell=True)

    #reset nvme to default
    cmd = "sshpass ssh root@" + \
        node_ip_addr +" 'yes | hdm reset-to-defaults --path " + dev + "'"

    print(cmd)
    call(cmd, shell=True)

def reset_all_nodes_nvme(nodes):
    #add hdms scan before rest to defaults
    for name, node in natsort.natsorted(nodes.items()):
        print("Reseting all NVME on node: " + name + " ...")
        reset_nvme(node.ip_addr, "/dev/nvme0")
        reset_nvme(node.ip_addr, "/dev/nvme1")
        print("Reset done")


def delete_namespaces(node_ip_addr, dev):
    #after reset there is only one namespace
    cmd = "sshpass ssh root@" + \
          node_ip_addr + " 'hdm scan'"

    print(cmd)
    call(cmd, shell=True)

    cmd = "sshpass ssh root@" + \
        node_ip_addr +" 'yes | hdm manage-namespaces --delete --id 1 --path " +\
        dev + "'"

    print(cmd)
    call(cmd, shell=True)

def delete_all_nodes_namespaces(nodes):
    for name, node in natsort.natsorted(nodes.items()):
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
    cmd = "sshpass ssh root@" + \
          node_ip_addr + " 'hdm scan'"

    print(cmd)
    call(cmd, shell=True)

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

    ns_size = NVME_SIZE / ((num_nodes + 1) / 2)

    for name, node in natsort.natsorted(nodes.items()):
        print("Create NVME namespaces on node: " + name + " ...")
        create_namespaces(node.ip_addr, ns_size, num_nodes)
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

    # cmd = "sshpass ssh root@" + \
    #       node.ip_addr + " 'echo 4096 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages'"
    #
    # print(cmd)
    # call(cmd, shell=True)
    #
    # cmd = "sshpass ssh root@" + \
    #       node.ip_addr + " 'echo 4096 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages'"
    # print(cmd)
    # call(cmd, shell=True)

    #firstly kill all possible tgts
    # cmd = "sshpass ssh root@" + node.ip_addr + \
    #       " \'killall /root/spdk/app/nvmf_tgt/nvmf_tgt\'"
    #
    # print(cmd)
    # call(cmd, shell=True)

    #run nvmf target
    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \'nohup /root/spdk/app/nvmf_tgt/nvmf_tgt -c /root/spdk/etc/spdk/nvmf.rain.in > /dev/null 2> /dev/null < /dev/null &\'"

    print(cmd)
    call(cmd, shell=True)


def reset_spdk(nodes):
    #rescan using spdk
    for name, node in natsort.natsorted(nodes.items()):
        cmd = "sshpass ssh root@" + node.ip_addr + \
              " \'/root/spdk/scripts/setup.sh reset\'"

        print(cmd)
        call(cmd, shell=True)

        cmd = "sshpass ssh root@" + \
              node.ip_addr + " 'hdm scan'"

        print(cmd)
        call(cmd, shell=True)


def create_all_nodes_tgts(nodes):
    for name, node in natsort.natsorted(nodes.items()):
        print("Create NVMF target on node: " + name + " ...")
        create_nvmf_target(node)
        time.sleep(5)
        print("Create NVMF target done")


def connect_nvmf_targets(cur_node, nodes):
    for name, node in natsort.natsorted(nodes.items()):
        #
        # cmd = "sshpass ssh root@" + cur_node.ip_addr + \
        #       " \' ping " + node.ib_addr1 + " -c 4\'"
        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
              " \'nohup ping " + node.ib_addr1 + "  > /dev/null 2> /dev/null &\'"
        print(cmd)
        call(cmd, shell=True)

        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
              " \' nvme discover -t rdma -a " + \
            node.ib_addr1 +" -s 4420\'"

        print(cmd)
        #call(cmd, shell=True)
        # p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        # out, err = p.communicate()
        # print(out)
        # print(err)
        run_cmd(cmd, 5)


        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
             " \' nvme connect -t rdma -n nqn.2016-06.io.spdk." + \
             node.name +"_1 -a " + node.ib_addr1 + " -s 4420 \'"

        print(cmd)
        call(cmd, shell=True)

        time.sleep(1)

        # cmd = "sshpass ssh root@" + cur_node.ip_addr + \
        #       " \' ping " + node.ib_addr2 + " -c 4\'"
        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
        " \'nohup ping " + node.ib_addr2 + "  > /dev/null 2> /dev/null &\'"

        print(cmd)
        call(cmd, shell=True)

        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
              " \' nvme discover -t rdma -a " + \
            node.ib_addr2 +" -s 4421 \'"

        print(cmd)
        #call(cmd, shell=True)
        # p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        # out, err = p.communicate()
        # print(out)
        # print(err)
        run_cmd(cmd, 5)

        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
             " \' nvme connect -t rdma -n nqn.2016-06.io.spdk." + \
             node.name +"_2 -a " + node.ib_addr2 + " -s 4421 \'"

        print(cmd)
        call(cmd, shell=True)

        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
              " \'killall -w ping \'"

        print(cmd)
        call(cmd, shell=True)

def connect_all_nodes_tgts(nodes):
    for name, node in natsort.natsorted(nodes.items()):
        print("Connecting NVMF target on node: " + name + " ...")
        connect_nvmf_targets(node, nodes)
        print("Connecting NVMF target done")


def disconnect_nvmf_targets(cur_node, nodes):
    for name, node in natsort.natsorted(nodes.items()):

        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
              " \' nvme disconnect -n nqn.2016-06.io.spdk." + \
              node.name + "_1 \'"

        print(cmd)
        call(cmd, shell=True)

        cmd = "sshpass ssh root@" + cur_node.ip_addr + \
              " \' nvme disconnect -n nqn.2016-06.io.spdk." + \
              node.name + "_2 \'"

        print(cmd)
        call(cmd, shell=True)

def disconnect_all_nodes_tgts(nodes):
    for name, node in natsort.natsorted(nodes.items()):
        print("Disonnecting NVMF target on node: " + name + " ...")
        disconnect_nvmf_targets(node, nodes)
        print("disconnecting NVMF target done")

def create_zfs_vol(node, nodes, ns_shift):
    num_nodes = len(nodes)

    ns_size = NVME_SIZE / ((num_nodes + 1) / 2)

    dev_list = ""
    num_nodes = len(nodes)

    cmd = "sshpass ssh root@" + node.ip_addr +\
              " 'lsblk | grep nvme | cut --delimiter=\" \" -f 1'"
    p = Popen(cmd , stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    out_str = out.decode("utf-8")
    err_str = err.decode("utf-8")

    all_nvme = out_str.split("\n")
    all_nvme = natsort.natsorted(all_nvme)
    all_nvme.remove("")

    for i in range(0, len(all_nvme), num_nodes):
        dev_list += "/dev/" + all_nvme[i + ns_shift] + " "

    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \' modprobe zfs\'"

    print(cmd)
    call(cmd, shell=True)

    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \' zpool create -o ashift=12 tank " + dev_list + " \'"

    print(cmd)
    call(cmd, shell=True)

    cmd = "sshpass ssh root@" + node.ip_addr + \
          " \' zfs create -b 4KB -V " + str(ns_size) + "gb tank/myvol \'"

    print(cmd)
    call(cmd, shell=True)

def create_all_nodes_zfs(nodes):
    ns_shift = 0
    for name, node in natsort.natsorted(nodes.items()):
        print("Createing ZFS on node: " + name + " ...")
        create_zfs_vol(node, nodes, ns_shift)
        ns_shift += 1
        print("Creating ZFS done")

def destroy_all_nodes_zfs(nodes):
    for name, node in natsort.natsorted(nodes.items()):
        print("Destroy zpool on node: " + name + " ...")
        cmd = "sshpass ssh root@" + node.ip_addr + \
              " \' zpool destroy tank \'"

        print(cmd)
        call(cmd, shell=True)
        print("Destroy zpool done")

def main():
    nodes = load_conf("nodes.conf")
    disconnect_all_nodes_tgts(nodes)
    #reset_all_nodes_nvme(nodes)
    #delete_all_nodes_namespaces(nodes)
    #create_all_nodes_namespaces(nodes)

    #create_all_nodes_tgts(nodes)
    #connect_all_nodes_tgts(nodes)

    #create_all_nodes_zfs(nodes)
    destroy_all_nodes_zfs(nodes)

    #disconnect_all_nodes_tgts(nodes)

    return 0

if __name__ == "__main__":
    #run main script
    main()

    print("don.")
