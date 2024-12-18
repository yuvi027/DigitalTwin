#!/bin/bash


for i in {1..4}; do
	echo "Dumping flows from s$i"
	sudo ovs-ofctl dump-flows s$i > flows_s$i.txt
done
echo "Done"
