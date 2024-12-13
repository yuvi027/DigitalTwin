from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
import subprocess

class Topology(Topo):
    def __init__(self):
        # initialize topology
        Topo.__init__(self)

        switch_link = {}
        host_link = {}

        # create switches
        for i in range(1, 4):
            self.addSwitch("s"+str(i))

        # create student hosts
        for i in range(1, 3):
            self.addHost("student"+str(i))

        # create researcher hosts
        for i in range(1, 3):
            self.addHost("r"+str(i))

        # adding links
        self.addLink("s1", "s2", **switch_link)
        self.addLink("s1", "s3", **switch_link)

        self.addLink("s1", "student1", **host_link)
        self.addLink("s3", "student2", **host_link)
        self.addLink("s1", "r1", **host_link)
        self.addLink("s3", "r2", **host_link)

topos = {"slicetopo": (lambda:Topology())}
   

if __name__ == "__main__":
    topo = Topology()
    #controller = RemoteController("c0", ip = "127.0.0.1", port = 6633)
    net = Mininet(
            topo = topo,
            controller = RemoteController("c0", ip = "127.0.0.1", port = 6633),
            switch = OVSKernelSwitch,
            build = False,
            autoSetMacs = True,
            autoStaticArp = True,
            link = TCLink)

    net.build()
    net.start()

    CLI(net)
    net.stop()
