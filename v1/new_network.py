from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

class NetworkSlicingTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Host configurations
        student_hosts = [("St1", "10.0.0.1"), ("St2", "10.0.0.2")]
        researcher_hosts = [("R1", "10.0.0.3"), ("R2", "10.0.0.4")]

        # Add switches
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")
        s4 = self.addSwitch("s4")

        # Add student hosts and connect to switches
        for i, (host, ip) in enumerate(student_hosts):
            h = self.addHost(host, ip=ip, defaultRoute=None)
            self.addLink(h, s1 if i == 0 else s3)

        # Add researcher hosts and connect to switches
        for i, (host, ip) in enumerate(researcher_hosts):
            h = self.addHost(host, ip=ip, defaultRoute=None)
            self.addLink(h, s1 if i == 0 else s3)

        # Connect switches
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s1, s4)
        self.addLink(s4, s3)
        self.addLink(s1, s3)  # Shared slice link

topos = {"networkslicingtopo": (lambda: NetworkSlicingTopo())}

if __name__ == "__main__":
    net = Mininet(
        topo=NetworkSlicingTopo(),
        switch=OVSKernelSwitch,
        controller=RemoteController("c0", ip="127.0.0.1", port=6633),
        link=TCLink,
        build=False,
        autoSetMacs=True,
    )

    net.build()
    net.start()
    CLI(net)
    net.stop()
