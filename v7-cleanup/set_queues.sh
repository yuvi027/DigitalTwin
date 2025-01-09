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
	queues:123=@q1 \
	queues:234=@q2 -- \
	--id=@q1 create queue other-config:min-rate=100000 other-config:max-rate=5000000000 -- \
	--id=@q2 create queue other-config:min-rate=100000 other-config:max-rate=5000000000 -- 

