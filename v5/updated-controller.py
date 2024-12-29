import threading
import time
import subprocess
import sys
import os
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp

def kill_existing_controllers():
    try:
        # Kill any existing Ryu processes
        subprocess.run(['pkill', '-f', 'ryu-manager'], 
                     stderr=subprocess.DEVNULL)
        time.sleep(1)  # Wait for processes to be killed
    except Exception as e:
        print(f"Warning: Could not kill existing controllers: {e}")

class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)
        self.exam_mode = False
        self.simulation_mode = False
        # Start with default configuration
        self.execute_script("setup_default")
        # Start control thread
        self.start_control_thread()

    def start_control_thread(self):
        def control_loop():
            while True:
                time.sleep(5)
                try:
                    print("\nNetwork Control Panel")
                    exam = input("Enable exam mode (true/false): ").lower() == 'true'
                    simulation = input("Enable simulation mode (true/false): ").lower() == 'true'
                    self.update_network_state(exam, simulation)
                except Exception as e:
                    print(f"Error in control loop: {e}")

        control_thread = threading.Thread(target=control_loop, daemon=True)
        control_thread.start()

    def execute_script(self, function_name):
        """Execute the appropriate shell script function"""
        try:
            subprocess.run(['bash', '-c', f'source ./traffic_control.sh && {function_name}'],
                         check=True)
            print(f"Successfully executed {function_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {function_name}: {e}")

    def update_network_state(self, exam, simulation):
        """Update network state based on mode changes"""
        if self.exam_mode == exam and self.simulation_mode == simulation:
            print("No state change needed")
            return

        self.exam_mode = exam
        self.simulation_mode = simulation

        if exam and simulation:
            self.execute_script("setup_exam_simulation")
        elif exam:
            self.execute_script("setup_default")
            self.execute_script("setup_exam_rules")
        elif simulation:
            self.execute_script("setup_simulation")
        else:
            self.execute_script("setup_default")

        print(f"\nNetwork state updated:")
        print(f"Exam mode: {exam}")
        print(f"Simulation mode: {simulation}")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch connection/reconnection"""
        # Re-apply current configuration when a switch connects/reconnects
        if self.exam_mode and self.simulation_mode:
            self.execute_script("setup_exam_simulation")
        elif self.exam_mode:
            self.execute_script("setup_default")
            self.execute_script("setup_exam_rules")
        elif self.simulation_mode:
            self.execute_script("setup_simulation")
        else:
            self.execute_script("setup_default")
