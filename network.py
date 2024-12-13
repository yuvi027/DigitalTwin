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
        
        host_config = dict(inNamespace=True)
        switch_link = dict()
        host_link = dict()

        # create switches
        for i in range(1, 5):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s"+str(i), **sconfig)

        # create student hosts
        for i in range(1, 3):
            self.addHost("student"+str(i), ip="10.0.0."+str(i)+"/24", **host_config)

        # create researcher hosts
        for j in range(1, 3):
            self.addHost("r"+str(j), ip="10.0.0."+str(j+2)+"/24",**host_config)

        # connecting switches
#        self.addLink("s1", "s2", **switch_link)
#        self.addLink("s1", "s3", **switch_link)
#        self.addLink("s1", "s4", **switch_link)

#        self.addLink("s2", "s3", **switch_link)
#        self.addLink("s4", "s3", **switch_link)

        # connecting hosts
#        self.addLink("student1", "s1", **host_link)
#        self.addLink("student2", "s3", **host_link)
#        self.addLink("r1", "s1", **host_link)
#        self.addLink("r2", "s3", **host_link)
        
        # connecting switches
        self.addLink("s1", "s2", intfName1="s1-eth3", intfName2="s2-eth1", **switch_link)
        self.addLink("s1", "s3", intfName1="s1-eth4", intfName2="s3-eth4", **switch_link)
        self.addLink("s1", "s4", intfName1="s1-eth5", intfName2="s4-eth1", **switch_link)

        self.addLink("s2", "s3", intfName1="s2-eth2", intfName2="s3-eth3", **switch_link)
        self.addLink("s4", "s3", intfName1="s4-eth2", intfName2="s3-eth5", **switch_link)

        # connecting hosts
        self.addLink("student1", "s1", intfName1="student1-eth1", intfName2="s1-eth1", **host_link)
        self.addLink("student2", "s3", intfName1="student2-eth1", intfName2="s3-eth1", **host_link)
        self.addLink("r1", "s1", intfName1="r1-eth1", intfName2="s1-eth2", **host_link)
        self.addLink("r2", "s3", intfName1="r2-eth1", intfName2="s3-eth2", **host_link)


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

    # enabling STP
    for switch in net.switches:
        switch.cmd('ovs-vsctl set bridge {} stp_enable=true'.format(switch.name))

    CLI(net)
    net.stop()
