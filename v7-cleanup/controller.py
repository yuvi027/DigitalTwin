import threading
import subprocess
import socket
import json
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet

class TrafficSlicing(app_manager.RyuApp):
    """
    SDN Controller for network traffic slicing with exam and simulation modes.
    Handles dynamic network reconfiguration through socket-based commands.
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        """Initialize the controller with default settings and start socket server."""
        super(TrafficSlicing, self).__init__(*args, **kwargs)
        
        # Network mode flags
        self.exam_mode = False
        self.simulation_mode = False

        # Port mapping for network slices
        # Format: {switch_id: {in_port: out_port}}
        self.slice_to_port = {
            1: {1: 3, 3: 1, 2: 4, 4: 2},  # Switch 1 mappings
            4: {1: 3, 3: 1, 2: 4, 4: 2},  # Switch 4 mappings
            2: {1: 2, 2: 1},              # Switch 2 mappings
            3: {1: 2, 2: 1},              # Switch 3 mappings
        }

        # Start socket server in separate thread
        self.socket_thread = threading.Thread(target=self.user_input_handler)
        self.socket_thread.daemon = True
        self.socket_thread.start()

    def clear_flows_and_queues(self):
        """
        Remove all flow entries and QoS configurations from switches.
        Only clears QoS on edge switches (s1 and s4).
        """
        try:
            # Clear all flow entries from all switches
            for switch in ['s1', 's2', 's3', 's4']:
                subprocess.run(['sudo', 'ovs-ofctl', 'del-flows', switch])
                
                # Clear QoS configurations only on edge switches
                if switch in ["s1", "s4"]:
                    subprocess.run(['sudo', 'ovs-vsctl', 'clear', 'port', f'{switch}-eth1', 'qos'])
                    subprocess.run(['sudo', 'ovs-vsctl', 'clear', 'port', f'{switch}-eth2', 'qos'])
        except subprocess.CalledProcessError as e:
            print(f"Error clearing flows and queues: {e}")

    def execute_shell_script(self, script_name):
        """Execute a shell script with sudo privileges."""
        try:
            subprocess.run(['sudo', 'bash', script_name], check=True)
            print(f"Successfully executed {script_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script_name}: {e}")

    def update_network_state(self, exam, simulation):
        """
        Update network configuration based on exam and simulation mode flags.
        
        Args:
            exam (bool): Whether to enable exam mode
            simulation (bool): Whether to enable simulation mode
        """
        # Skip if no state change
        if self.exam_mode == exam and self.simulation_mode == simulation:
            print("No state change needed")
            return

        # Update mode flags
        self.exam_mode = exam
        self.simulation_mode = simulation
        
        # Reset network state
        self.clear_flows_and_queues()

        # Apply appropriate configuration
        if exam and simulation:
            self.execute_shell_script("scenarios/exam_and_simulation.sh")
        elif exam:
            self.execute_shell_script("scenarios/exam.sh")
        elif simulation:
            self.execute_shell_script("scenarios/simulation.sh")
        else:
            self.execute_shell_script("scenarios/miss_flow.sh")

        print(f"\nNetwork state updated:")
        print(f"Exam mode: {exam}")
        print(f"Simulation mode: {simulation}")

    def user_input_handler(self):
        """
        Socket server to handle network mode changes from external clients.
        Listens on port 9999 for JSON commands.
        """
        def handle_client(client_socket):
            """Handle individual client connections."""
            try:
                with client_socket:
                    data = client_socket.recv(1024).decode("utf-8").strip()
                    if data:
                        try:
                            message = json.loads(data)
                            exam = message["exam"].lower() == "true"
                            simulation = message["simulation"].lower() == "true"
                            self.update_network_state(exam, simulation)
                        except json.JSONDecodeError:
                            print("Invalid JSON received")
            except Exception as e:
                print(f"Error in socket handler: {e}")

        # Set up and run socket server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", 9999))
        server.listen(5)
        print("Server listening on port 9999")

        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Handle switch connection events and install default flow entries.
        Called when a switch connects or reconnects to the controller.
        """
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Reapply current configuration if in a special mode
        if self.exam_mode or self.simulation_mode:
            self.update_network_state(self.exam_mode, self.simulation_mode)

    def add_flow(self, datapath, priority, match, actions):
        """
        Install a flow entry in a switch.
        
        Args:
            datapath: Switch connection object
            priority: Priority of the flow rule
            match: Flow match conditions
            actions: Actions to be executed for matching packets
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                           actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                               match=match, instructions=inst)
        datapath.send_msg(mod)

    def _send_package(self, msg, datapath, in_port, actions):
        """
        Send a packet out through the switch.
        
        Args:
            msg: data
            datapath: Switch connection object
            in_port: Input port number
            actions: Actions to be applied to the packet
        """
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
        """
        Handle incoming packets that don't match any flow entries.
        Installs appropriate flow rules based on the slice configuration.
        """
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match["in_port"]
        dpid = datapath.id

        # Determine output port based on slice configuration
        out_port = self.slice_to_port[dpid][in_port]
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        match = datapath.ofproto_parser.OFPMatch(in_port=in_port)

        # Install flow rule and forward packet
        self.add_flow(datapath, 1, match, actions)
        self._send_package(msg, datapath, in_port, actions)