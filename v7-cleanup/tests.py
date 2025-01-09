#!/usr/bin/python3

import subprocess
import time
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import threading
import re

class NetworkTester:
    def __init__(self, net):
        self.net = net
        self.st1 = net.get('St1')
        self.st2 = net.get('St2')
        self.r1 = net.get('R1')
        self.r2 = net.get('R2')
        
    def test_connectivity(self, h1, h2, expected_success=True):
        """Test basic connectivity between two hosts"""
        result = h1.cmd(f'ping -c 3 {h2.IP()}')
        success = '0% packet loss' in result
        assert success == expected_success, f"Connectivity test failed between {h1.name} and {h2.name}"
        return success

    def test_bandwidth(self, sender, receiver, port=5001, time=10, expected_bw=None):
        """Test bandwidth between two hosts using iperf"""
        # Start iperf server
        receiver.cmd(f'iperf -s -p {port} &')
        time.sleep(1)
        
        # Run iperf client
        result = sender.cmd(f'iperf -c {receiver.IP()} -p {port} -t {time}')
        
        # Kill iperf server
        receiver.cmd('killall -9 iperf')
        
        # Extract bandwidth from result
        bw = float(re.findall(r'(\d+\.?\d*) Mbits/sec', result)[-1])
        
        if expected_bw:
            assert abs(bw - expected_bw) < expected_bw * 0.1, f"Bandwidth {bw} Mbits/sec differs from expected {expected_bw} Mbits/sec"
        
        return bw

    def test_simulation_traffic(self, sender, receiver, expected_success=True):
        """Test simulation traffic (port 6000)"""
        # Start netcat listener
        receiver.cmd('nc -l 6000 > /dev/null &')
        time.sleep(1)
        
        # Send test data
        result = sender.cmd(f'echo "test" | nc {receiver.IP()} 6000 -w 1')
        success = result == ""  # Empty result means successful transmission
        
        # Kill netcat
        receiver.cmd('killall -9 nc')
        
        assert success == expected_success, f"Simulation traffic test failed between {sender.name} and {receiver.name}"
        return success

    def run_default_mode_tests(self):
        """Test default mode (exam=False, simulation=False)"""
        info("*** Testing Default Mode ***\n")
        
        # Test basic connectivity
        self.test_connectivity(self.st1, self.st2)
        self.test_connectivity(self.r1, self.r2)
        
        # Test bandwidth (should be full capacity)
        bw = self.test_bandwidth(self.st1, self.st2)
        info(f"Student bandwidth: {bw} Mbits/sec\n")
        
        bw = self.test_bandwidth(self.r1, self.r2)
        info(f"Researcher bandwidth: {bw} Mbits/sec\n")

    def run_exam_mode_tests(self):
        """Test exam mode (exam=True, simulation=False)"""
        info("*** Testing Exam Mode ***\n")
        
        # Test student connectivity (should fail)
        self.test_connectivity(self.st1, self.st2, expected_success=False)
        
        # Test researcher connectivity through researcher slice
        self.test_connectivity(self.r1, self.r2)
        
        # Test researcher bandwidth
        bw = self.test_bandwidth(self.r1, self.r2)
        info(f"Researcher bandwidth: {bw} Mbits/sec\n")

    def run_simulation_mode_tests(self):
        """Test simulation mode (exam=False, simulation=True)"""
        info("*** Testing Simulation Mode ***\n")
        
        # Test regular traffic with QoS
        bw_student = self.test_bandwidth(self.st1, self.st2, expected_bw=5000)
        info(f"Student bandwidth: {bw_student} Mbits/sec\n")
        
        bw_researcher = self.test_bandwidth(self.r1, self.r2, expected_bw=5000)
        info(f"Researcher bandwidth: {bw_researcher} Mbits/sec\n")
        
        # Test simulation traffic
        self.test_simulation_traffic(self.r1, self.r2)

    def run_both_modes_tests(self):
        """Test both modes (exam=True, simulation=True)"""
        info("*** Testing Both Modes ***\n")
        
        # Test student connectivity (should fail)
        self.test_connectivity(self.st1, self.st2, expected_success=False)
        
        # Test researcher normal traffic
        self.test_connectivity(self.r1, self.r2)
        
        # Test simulation traffic
        self.test_simulation_traffic(self.r1, self.r2)
        
        # Test researcher bandwidth
        bw = self.test_bandwidth(self.r1, self.r2)
        info(f"Researcher bandwidth: {bw} Mbits/sec\n")

def run_tests(network_state):
    """Run appropriate tests based on network state"""
    net = Mininet(controller=RemoteController)
    tester = NetworkTester(net)
    
    if network_state == "default":
        tester.run_default_mode_tests()
    elif network_state == "exam":
        tester.run_exam_mode_tests()
    elif network_state == "simulation":
        tester.run_simulation_mode_tests()
    elif network_state == "both":
        tester.run_both_modes_tests()
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    
    # Test all scenarios
    states = ["default", "exam", "simulation", "both"]
    for state in states:
        info(f"\n\nTesting {state} mode\n")
        run_tests(state)
