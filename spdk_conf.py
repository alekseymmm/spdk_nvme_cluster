
def create_nvmf_config(node):
    with open("nvmf.tgt.in", "r") as template:
        with open("nvmf.rain.in", "w") as config:
            for line in template:
                if(line == "NQN1...\n"):
                    line = "NQN nqn.2016-06.io.spdk." + node.name + "_1\n"
                if (line == "Listen1...\n"):
                    line = "Listen RDMA " + node.ib_addr1 + ":4420\n"
                if(line == "NQN2...\n"):
                    line = "NQN nqn.2016-06.io.spdk." + node.name + "_2\n"
                if (line == "Listen2...\n"):
                    line = "Listen RDMA " + node.ib_addr2 + ":4420\n"
                config.write(line)

    config.close();
    template.close()