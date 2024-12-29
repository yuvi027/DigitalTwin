#!/bin/bash

# default_setup.sh - Base configuration script
setup_default() {
    # Clear existing flows
    for sw in s1 s2 s3 s4; do
        ovs-ofctl del-flows $sw
    done

    # Setup shared slice (s1-s2-s4 path)
    ovs-ofctl add-flow s1 "priority=1,in_port=1,actions=output:2"  # St1 -> s2
    ovs-ofctl add-flow s1 "priority=1,in_port=2,actions=output:1"  # s2 -> St1
    ovs-ofctl add-flow s2 "priority=1,in_port=1,actions=output:2"  # s1 -> s4
    ovs-ofctl add-flow s2 "priority=1,in_port=2,actions=output:1"  # s4 -> s1
    ovs-ofctl add-flow s4 "priority=1,in_port=2,actions=output:4"  # s2 -> St2
    ovs-ofctl add-flow s4 "priority=1,in_port=4,actions=output:2"  # St2 -> s2

    # Setup researcher slice (s1-s3-s4 path)
    ovs-ofctl add-flow s1 "priority=1,in_port=4,actions=output:3"  # R1 -> s3
    ovs-ofctl add-flow s1 "priority=1,in_port=3,actions=output:4"  # s3 -> R1
    ovs-ofctl add-flow s3 "priority=1,in_port=1,actions=output:2"  # s1 -> s4
    ovs-ofctl add-flow s3 "priority=1,in_port=2,actions=output:1"  # s4 -> s1
    ovs-ofctl add-flow s4 "priority=1,in_port=3,actions=output:6"  # s3 -> R2
    ovs-ofctl add-flow s4 "priority=1,in_port=6,actions=output:3"  # R2 -> s3
}

# exam_rules.sh - Additional rules for exam mode
setup_exam_rules() {
    # Drop all student traffic
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.1,actions=drop"  # Drop St1
    ovs-ofctl add-flow s4 "priority=2,ip,nw_src=10.0.0.2,actions=drop"  # Drop St2
}

# simulation_setup.sh - Complete setup for simulation mode
setup_simulation() {
    # Clear existing flows
    for sw in s1 s2 s3 s4; do
        ovs-ofctl del-flows $sw
    done

    # Setup QoS queues on shared slice
    for sw in s1 s2 s4; do
        ovs-vsctl -- set port ${sw}-eth1 qos=@newqos -- \
        --id=@newqos create qos type=linux-htb \
        queues:1=@q1 queues:2=@q2 -- \
        --id=@q1 create queue other-config:max-rate=5000000 -- \
        --id=@q2 create queue other-config:max-rate=5000000
    done

    # Route simulation traffic (port 5000) to researcher slice
    ovs-ofctl add-flow s1 "priority=3,tcp,tp_dst=5000,actions=output:3"  # To s3
    ovs-ofctl add-flow s3 "priority=3,tcp,tp_dst=5000,actions=output:2"  # To s4
    ovs-ofctl add-flow s4 "priority=3,tcp,tp_dst=5000,actions=output:6"  # To R2

    # Route normal traffic through shared slice with QoS
    # Researcher traffic to queue 1
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.3,actions=set_queue:1,output:2"
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.4,actions=set_queue:1,output:2"
    
    # Student traffic to queue 2
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.1,actions=set_queue:2,output:2"
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.2,actions=set_queue:2,output:2"
}

# exam_simulation_setup.sh - Setup for both modes
setup_exam_simulation() {
    # Clear existing flows
    for sw in s1 s2 s3 s4; do
        ovs-ofctl del-flows $sw
    done

    # Route simulation traffic to researcher slice
    ovs-ofctl add-flow s1 "priority=3,tcp,tp_dst=5000,actions=output:3"
    ovs-ofctl add-flow s3 "priority=3,tcp,tp_dst=5000,actions=output:2"
    ovs-ofctl add-flow s4 "priority=3,tcp,tp_dst=5000,actions=output:6"

    # Route researcher communication to shared slice
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.3,actions=output:2"
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.4,actions=output:2"
    
    # Drop all student traffic
    ovs-ofctl add-flow s1 "priority=2,ip,nw_src=10.0.0.1,actions=drop"
    ovs-ofctl add-flow s4 "priority=2,ip,nw_src=10.0.0.2,actions=drop"
}
