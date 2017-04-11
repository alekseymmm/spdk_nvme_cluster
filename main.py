
from subprocess import call

NVME_SIZE = 1600 # GB

class Node:
    def __init__(self, name, ip_addr, ib_addr):
        self.name = name
        self.ip_addr = ip_addr
        self.ib_addr = ib_addr

def reset_nvme(node_ip_addr, dev):
    #reset nvme to default
    cmd = "\n\nsshpass ssh root@" + \
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
    cmd = "\n\nsshpass ssh root@" + \
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

            [name, ip_addr, ib_addr] = line.split(" ")
            new_node = Node(name, ip_addr, ib_addr)
            nodes[name] = new_node

    return nodes

def main():
    nodes = load_conf("nodes.conf")
    #reset_all_nodes_nvme(nodes)
    delete_all_nodes_namespaces(nodes)

    return

if __name__ == "__main__":
    #run main script
    main()
    print("done.")
