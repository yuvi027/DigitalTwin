#!/bin/bash

echo "Setting up exam mode configuration"

# Drop all student traffic
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.2,idle_timeout=0,actions=drop