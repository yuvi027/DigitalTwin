#!/bin/sh

echo "Installing flows in switch 1"

# From student1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=1,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:3
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=1,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=1,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:3

# To student1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=3,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=4,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=5,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=2,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1

# From researcher1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=2,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:5
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=2,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=2,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:5

# To researcher1
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=3,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=4,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=5,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s1 in_port=1,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:2

# ARP rule
sudo ovs-ofctl -O OpenFlow13 add-flow s1 arp,actions=flood

echo "Installing flows in switch 2"

# To student2
sudo ovs-ofctl -O OpenFlow13 add-flow s2 in_port=1,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:2
# To researcher2
sudo ovs-ofctl -O OpenFlow13 add-flow s2 in_port=1,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:2
# To student1
sudo ovs-ofctl -O OpenFlow13 add-flow s2 in_port=2,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1
# To researcher1
sudo ovs-ofctl -O OpenFlow13 add-flow s2 in_port=2,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:1

# ARP rule
sudo ovs-ofctl -O OpenFlow13 add-flow s2 arp,actions=flood

echo "Installing flows in switch 4"

# To student2
sudo ovs-ofctl -O OpenFlow13 add-flow s4 in_port=1,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:2
# To researcher2
sudo ovs-ofctl -O OpenFlow13 add-flow s4 in_port=1,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:2
# To student1
sudo ovs-ofctl -O OpenFlow13 add-flow s4 in_port=2,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1
# To researcher1
sudo ovs-ofctl -O OpenFlow13 add-flow s4 in_port=2,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:1

# ARP rule
sudo ovs-ofctl -O OpenFlow13 add-flow s4 arp,actions=flood

echo "Installing flows in switch 3"

# From student2
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=1,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:5
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=1,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:5
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=1,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:2

# To student2
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=3,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=2,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=5,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=4,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:1

# From researcher2
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=2,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:1
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=2,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:3
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=2,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:3

# To researcher2
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=3,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=4,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=5,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s3 in_port=1,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:2

# ARP rule
sudo ovs-ofctl -O OpenFlow13 add-flow s3 arp,actions=flood

