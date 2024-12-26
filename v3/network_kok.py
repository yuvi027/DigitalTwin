from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class NetworkSlicingTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        host_config = dict(inNamespace=True)
        researcher_link_config = dict(bw=10)
        student_link_config = dict(bw=10)
        host_link_config = dict()

        # Create switch nodes
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        # Create host nodes
        for i in range(2):
            self.addHost("St%d" % (i + 1), **host_config)
        
        for i in range(2):
            self.addHost("R%d" % (i + 1), **host_config)

        # Add switch links
        self.addLink("s1", "s2", **student_link_config)
        self.addLink("s2", "s4", **student_link_config)
        self.addLink("s1", "s3", **researcher_link_config)
        self.addLink("s3", "s4", **researcher_link_config)

        # Add host links
        self.addLink("St1", "s1", **host_link_config)
        self.addLink("R1", "s1", **host_link_config)
        self.addLink("St2", "s4", **host_link_config)
        self.addLink("R2", "s4", **host_link_config)


topos = {"networkslicingtopo": (lambda: NetworkSlicingTopo())}

if __name__ == "__main__":
    topo = NetworkSlicingTopo()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.build()
    net.start()
    CLI(net)
    net.stop()
