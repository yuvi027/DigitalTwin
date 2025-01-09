from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class NetworkSlicingTopo(Topo):
    """
    Custom topology class for network slicing implementation.
    Creates a network with:
    - 4 switches in a diamond topology
    - 2 student hosts (St1, St2)
    - 2 researcher hosts (R1, R2)
    - Separate paths for student and researcher traffic
    """

    def __init__(self):
        """Initialize the network topology with switches, hosts, and links."""
        # Initialize parent class
        Topo.__init__(self)

        # Configuration dictionaries
        # Host namespace configuration
        host_config = dict(inNamespace=True)
        
        # Link configurations with bandwidth specifications
        researcher_link_config = dict(bw=10)  # 10 Mbps for researcher path
        student_link_config = dict(bw=10)     # 10 Mbps for student path
        host_link_config = dict()             # Default configuration for host links

        self._create_switches()
        self._create_hosts(host_config)
        self._create_network_links(student_link_config, researcher_link_config, host_link_config)

    def _create_switches(self):
        """
        Create four OpenFlow switches (s1-s4) in a diamond topology.
        Each switch gets a unique dpid in hexadecimal format.
        """
        for i in range(4):
            switch_number = i + 1
            # Create dpid as 16-char hex string
            switch_config = {"dpid": f"{switch_number:016x}"}
            self.addSwitch(f"s{switch_number}", **switch_config)

    def _create_hosts(self, host_config):
        """
        Create student and researcher hosts with specific IP addresses.
        
        Args:
            host_config: Dictionary containing host configuration parameters
        """
        # Create student hosts (St1, St2)
        for i in range(2):
            host_number = i + 1
            self.addHost(
                f"St{host_number}",
                ip=f"10.0.0.{host_number}/24",
                **host_config
            )
        
        # Create researcher hosts (R1, R2)
        for i in range(2):
            host_number = i + 1
            self.addHost(
                f"R{host_number}",
                ip=f"10.0.0.{i + 3}/24",  # IPs start at 10.0.0.3
                **host_config
            )

    def _create_network_links(self, student_link_config, researcher_link_config, host_link_config):
        """
        Create network links between switches and hosts.
        
        Args:
            student_link_config: Configuration for student path links
            researcher_link_config: Configuration for researcher path links
            host_link_config: Configuration for host-to-switch links
        """
        # Create switch-to-switch links
        # Student path: s1 -> s2 -> s4
        self.addLink("s1", "s2", **student_link_config)
        self.addLink("s2", "s4", **student_link_config)
        
        # Researcher path: s1 -> s3 -> s4
        self.addLink("s1", "s3", **researcher_link_config)
        self.addLink("s3", "s4", **researcher_link_config)

        # Connect hosts to edge switches (s1 and s4)
        # s1 connections
        self.addLink("St1", "s1", **host_link_config)  # Student 1
        self.addLink("R1", "s1", **host_link_config)   # Researcher 1
        
        # s4 connections
        self.addLink("St2", "s4", **host_link_config)  # Student 2
        self.addLink("R2", "s4", **host_link_config)   # Researcher 2


# Register the topology class
topos = {
    "networkslicingtopo": (lambda: NetworkSlicingTopo())
}


if __name__ == "__main__":
    # Create the topology
    topo = NetworkSlicingTopo()
    
    # Create and configure the network
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,    # Use OpenVSwitch
        build=False,               # Don't build yet
        autoSetMacs=True,          # Set MAC addresses automatically
        autoStaticArp=True,        # Set static ARP entries
        link=TCLink,               # Use TC links for QoS
    )
    
    # Add the remote controller
    controller = RemoteController(
        name="c1",
        ip="127.0.0.1",  # localhost
        port=6633        # OpenFlow default port
    )
    net.addController(controller)
    
    # Build and start the network
    net.build()
    net.start()
    
    # Start the CLI
    CLI(net)
    
    # Clean up when done
    net.stop()