#!/bin/bash

echo "Setting up configuration for both exam and simulation modes"

echo "Setting up S1 configuration"
# Drop all student traffic
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.2,idle_timeout=0,actions=drop

# Researcher normal traffic through shared slice
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:1
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:4

# Simulation traffic through researcher slice R1 to R2
sudo ovs-ofctl add-flow s1 tcp,priority=10,nw_src=10.0.0.3,nw_dst=10.0.0.4,tp_dst=6000,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s1 tcp,priority=10,nw_src=10.0.0.4,nw_dst=10.0.0.3,tp_src=6000,idle_timeout=0,actions=output:4

# Simulation traffic through researcher slice R2 to R1
sudo ovs-ofctl add-flow s1 tcp,priority=10,nw_src=10.0.0.4,nw_dst=10.0.0.3,tp_dst=6000,idle_timeout=0,actions=output:4
sudo ovs-ofctl add-flow s1 tcp,priority=10,nw_src=10.0.0.3,nw_dst=10.0.0.4,tp_src=6000,idle_timeout=0,actions=output:2

echo "Setting up S2 configuration"
# Researcher normal traffic through shared slice
sudo ovs-ofctl add-flow s2 ip,priority=1,in_port=1,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s2 ip,priority=1,in_port=2,idle_timeout=0,actions=output:1

echo "Setting up S3 configuration"
# Simulation traffic through researcher slice
sudo ovs-ofctl add-flow s3 ip,priority=1,in_port=1,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s3 ip,priority=1,in_port=2,idle_timeout=0,actions=output:1

echo "Setting up S4 configuration"
# Simulation traffic through researcher slice R1 to R2
sudo ovs-ofctl add-flow s4 tcp,priority=10,nw_src=10.0.0.3,nw_dst=10.0.0.4,tp_dst=6000,idle_timeout=0,actions=output:4
sudo ovs-ofctl add-flow s4 tcp,priority=10,nw_src=10.0.0.4,nw_dst=10.0.0.3,tp_src=6000,idle_timeout=0,actions=output:2

# Simulation traffic through researcher slice R2 to R1
sudo ovs-ofctl add-flow s4 tcp,priority=10,nw_src=10.0.0.4,nw_dst=10.0.0.3,tp_dst=6000,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s4 tcp,priority=10,nw_src=10.0.0.3,nw_dst=10.0.0.4,tp_src=6000,idle_timeout=0,actions=output:4

# Researcher normal traffic through shared slice
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:4
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:1
