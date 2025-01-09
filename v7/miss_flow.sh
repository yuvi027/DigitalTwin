#!bin/bash

echo "Adding miss flow in switches"

for SWITCH in s1 s2 s3 s4; do
    sudo ovs-ofctl add-flow $SWITCH "priority=0,actions=CONTROLLER"
done

echo "Table-miss flows added to all switches."

