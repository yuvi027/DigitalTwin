#!/bin/bash

echo "Setting up exam mode configuration"

# Drop all student traffic
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.2,idle_timeout=0,actions=drop

# Researcher traffic through researcher slice only
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:4

# Adding port forwarding rule to s3
sudo ovs-ofctl add-flow s3 ip,priority=1,in_port=1,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s3 ip,priority=1,in_port=2,idle_timeout=0,actions=output:1

# Researcher traffic at s4
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:4
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:2
