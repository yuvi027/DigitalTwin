#!/bin/bash

echo "Creating queue on the student slice"

# Setting queue on s1
sudo ovs-vsctl set port s1-eth1 qos=@newqos -- \
	--id=@newqos create QoS type=linux-htb \
	other-config:max-rate=10000000000 \
	queues:123=@q1 \
	queues:234=@q2 -- \
	--id=@q1 create queue other-config:min-rate=100000 other-config:max-rate=5000000000 -- \
	--id=@q2 create queue other-config:min-rate=100000 other-config:max-rate=5000000000 -- 

# Setting queue on s4
sudo ovs-vsctl set port s4-eth1 qos=@newqos -- \
	--id=@newqos create QoS type=linux-htb \
	other-config:max-rate=10000000000 \
	queues:456=@q3 \
	queues:567=@q4 -- \
	--id=@q3 create queue other-config:min-rate=100000 other-config:max-rate=5000000000 -- \
	--id=@q4 create queue other-config:min-rate=100000 other-config:max-rate=5000000000 -- 

# Adding queue flow rules
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=set_queue:123,output:1
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=set_queue:234,output:1
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=output:3
sudo ovs-ofctl add-flow s1 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:4

sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=set_queue:456,output:1
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=set_queue:567,output:1
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=output:3
sudo ovs-ofctl add-flow s4 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:4

# Adding port forwarding rule to s2
sudo ovs-ofctl add-flow s2 ip,priority=1,in_port=1,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s2 ip,priority=1,in_port=2,idle_timeout=0,actions=output:1

# Adding flow rules for simulation traffic
sudo ovs-ofctl add-flow s1 tcp,priority=10,tp_dst=6000,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s1 tcp,priority=10,tp_src=6000,idle_timeout=0,actions=output:4

sudo ovs-ofctl add-flow s4 tcp,priority=10,tp_dst=6000,idle_timeout=0,actions=output:4
sudo ovs-ofctl add-flow s4 tcp,priority=10,tp_src=6000,idle_timeout=0,actions=output:2

# Adding port forwarding rule to s3
sudo ovs-ofctl add-flow s3 ip,priority=1,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=output:2
sudo ovs-ofctl add-flow s3 ip,priority=1,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=output:1
