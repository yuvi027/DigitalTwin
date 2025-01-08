#!/bin/bash

echo "Setting up default mode configuration"

# Adding queue flow rules

sudo ovs-ofctl add-flow s2 ip,priority=1,in_port=1,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s2 ip,priority=1,in_port=2,idle_timeout=0,actions=output:1

sudo ovs-ofctl add-flow s3 ip,priority=1,in_port=1,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s3 ip,priority=1,in_port=2,idle_timeout=0,actions=output:1

# Students
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=output:1
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=output:3

sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=output:3
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=output:1

# Researchers
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:4

sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:4
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:2