
from subprocess import call

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
    #reset_nvme(nodes["raidix12"].ip_addr, "/dev/nvme0")
    reset_all_nodes_nvme(nodes)
    
    return

if __name__ == "__main__":
    #run main script
    main()
    print("done.")
