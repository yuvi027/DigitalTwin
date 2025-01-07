import threading
import time
import subprocess
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp

class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)
        self.exam_mode = False
        self.simulation_mode = False

        # Start with default configuration (both false)
        self.slice_to_port = {
            1: {1: 3, 3: 1, 2: 4, 4: 2},
            4: {1: 3, 3: 1, 2: 4, 4: 2},
            2: {1: 2, 2: 1},
            3: {1: 2, 2: 1},
        }

        # Start control thread
        threading.Thread(target=self.user_input_handler, daemon=True).start()

    def clear_flows_and_queues(self):
        """Clear all flows and queues from switches"""
        try:
            for switch in ['s1', 's2', 's3', 's4']:
                subprocess.run(['sudo', 'ovs-ofctl', 'del-flows', switch])
                subprocess.run(['sudo', 'ovs-vsctl', 'clear', 'port', f'{switch}-eth1', 'qos'])
                subprocess.run(['sudo', 'ovs-vsctl', 'clear', 'port', f'{switch}-eth2', 'qos'])
        except subprocess.CalledProcessError as e:
            print(f"Error clearing flows and queues: {e}")

    def execute_shell_script(self, script_name):
        """Execute a shell script"""
        try:
            subprocess.run(['sudo', 'bash', script_name], check=True)
            print(f"Successfully executed {script_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script_name}: {e}")

    def update_network_state(self, exam, simulation):
        """Update network state based on exam and simulation modes"""
        if self.exam_mode == exam and self.simulation_mode == simulation:
            print("No state change needed")
            return

        self.exam_mode = exam
        self.simulation_mode = simulation
        
        # Clear existing configuration
        self.clear_flows_and_queues()

        # Apply new configuration based on modes
        if exam and simulation:
            self.execute_shell_script("exam_and_simulation.sh")
        elif exam:
            self.execute_shell_script("exam.sh")
        elif simulation:
            # self.execute_shell_script("set_queues.sh")
            self.execute_shell_script("simulation.sh")
        else:
            # Default mode - no scripts needed as controller handles basic forwarding
            pass

        print(f"\nNetwork state updated:")
        print(f"Exam mode: {exam}")
        print(f"Simulation mode: {simulation}")

    def user_input_handler(self):
        """Handle user input for mode changes"""
        while True:
            time.sleep(5)  # Wait before asking for input
            try:
                print("\nNetwork Control Panel")
                exam = input("Enable exam mode (true/false): ").lower() == 'true'
                simulation = input("Enable simulation mode (true/false): ").lower() == 'true'
                self.update_network_state(exam, simulation)
            except Exception as e:
                print(f"Error in user input handler: {e}")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch connection/reconnection"""
        print("switch_features_handler called")
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Reapply current configuration if needed
        if self.exam_mode or self.simulation_mode:
            self.update_network_state(self.exam_mode, self.simulation_mode)

    def add_flow(self, datapath, priority, match, actions):
        """Add a flow entry to the switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                           actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                               match=match, instructions=inst)
        datapath.send_msg(mod)

    
    def _send_package(self, msg, datapath, in_port, actions):
        data = None
        ofproto = datapath.ofproto
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=data,
        )
        datapath.send_msg(out)
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        print("_packet_in_handler called")
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match["in_port"]
        dpid = datapath.id

        out_port = self.slice_to_port[dpid][in_port]
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        match = datapath.ofproto_parser.OFPMatch(in_port=in_port)

        self.add_flow(datapath, 1, match, actions)
        self._send_package(msg, datapath, in_port, actions)
