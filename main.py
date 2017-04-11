
from subprocess import call

from setuptools import command


class Node:
    def __init__(self, name, ip_addr, ib_addr):
        self.name = name
        self.ip_addr = ip_addr
        self.ib_addr = ib_addr

def format_nvme(node_ip_addr, dev):
    #reset to default firstly
    command = ["yes | sshpass", "ssh root@" +
               node_ip_addr +" + hdm reset-to-defaults --path " + dev]
    print(command)
    call(command)

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
    
    return

if __name__ == "__main__":
    #run main script
    main()
    print("done.")
