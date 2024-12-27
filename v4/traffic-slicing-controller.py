import threading
import time
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp
from ryu.lib.packet import ether_types

class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)
        self.exam_mode = False
        self.simulation_mode = False
        self.student_ips = ['10.0.0.1', '10.0.0.2']
        self.researcher_ips = ['10.0.0.3', '10.0.0.4']
        self.simulation_port = 5000
        
        # Slice definitions
        self.shared_slice = {  # s1-s2-s4 path
            1: {1: 2, 2: 1},
            2: {1: 2, 2: 1},
            4: {2: 4, 4: 2}
        }
        
        self.researcher_slice = {  # s1-s3-s4 path
            1: {1: 3, 3: 1},
            3: {1: 2, 2: 1},
            4: {3: 4, 4: 3}
        }

        # Start control thread after initialization
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

    def update_network_state(self, exam, simulation):
        """Updates network state based on exam and simulation modes"""
        self.exam_mode = exam
        self.simulation_mode = simulation
        
        # Store previous datapaths to clear flows
        datapaths = [dp for dp in self.dpset.get_all() if dp is not None]
        
        for dp in datapaths:
            # Clear existing flows
            self.clear_all_flows(dp)
            
            # Install default flow for controller communication
            parser = dp.ofproto_parser
            ofproto = dp.ofproto
            match = parser.OFPMatch()
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(dp, 0, match, actions)
            
        print(f"\nNetwork state updated:")
        print(f"Exam mode: {exam}")
        print(f"Simulation mode: {simulation}")

    def clear_all_flows(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Clear all flows
        match = parser.OFPMatch()
        instructions = []
        flow_mod = parser.OFPFlowMod(
            datapath=datapath,
            command=ofproto.OFPFC_DELETE,
            out_port=ofproto.OFPP_ANY,
            out_group=ofproto.OFPG_ANY,
            match=match,
            instructions=instructions
        )
        datapath.send_msg(flow_mod)

    def setup_normal_flows(self, datapath, in_port, ip_src, ip_dst):
        # Use shared slice for all traffic
        if datapath.id in self.shared_slice and in_port in self.shared_slice[datapath.id]:
            out_port = self.shared_slice[datapath.id][in_port]
            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            match = datapath.ofproto_parser.OFPMatch(
                in_port=in_port,
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=ip_src,
                ipv4_dst=ip_dst
            )
            self.add_flow(datapath, 1, match, actions)
            return actions
        return []

    def setup_exam_simulation_flows(self, datapath, in_port, ip_src, ip_dst, tcp_port=None):
        parser = datapath.ofproto_parser
        actions = []

        if ip_src in self.researcher_ips:
            if tcp_port == self.simulation_port:  # Simulation traffic
                if datapath.id in self.researcher_slice and in_port in self.researcher_slice[datapath.id]:
                    out_port = self.researcher_slice[datapath.id][in_port]
                    actions = [parser.OFPActionOutput(out_port)]
            else:  # Regular researcher traffic
                if datapath.id in self.shared_slice and in_port in self.shared_slice[datapath.id]:
                    out_port = self.shared_slice[datapath.id][in_port]
                    actions = [
                        parser.OFPActionSetQueue(1),  # Queue 1: 50% bandwidth
                        parser.OFPActionOutput(out_port)
                    ]

        if actions:
            match = parser.OFPMatch(
                in_port=in_port,
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=ip_src,
                ipv4_dst=ip_dst,
                tcp_dst=tcp_port if tcp_port else 0
            )
            self.add_flow(datapath, 2, match, actions)
        return actions

    def setup_simulation_flows(self, datapath, in_port, ip_src, ip_dst, tcp_port=None):
        parser = datapath.ofproto_parser
        actions = []

        if tcp_port == self.simulation_port and ip_src in self.researcher_ips:
            # Simulation traffic goes through researcher slice
            if datapath.id in self.researcher_slice and in_port in self.researcher_slice[datapath.id]:
                out_port = self.researcher_slice[datapath.id][in_port]
                actions = [parser.OFPActionOutput(out_port)]
        else:
            # Regular traffic through shared slice with QoS
            if datapath.id in self.shared_slice and in_port in self.shared_slice[datapath.id]:
                out_port = self.shared_slice[datapath.id][in_port]
                queue_id = 1 if ip_src in self.researcher_ips else 2
                actions = [
                    parser.OFPActionSetQueue(queue_id),
                    parser.OFPActionOutput(out_port)
                ]

        if actions:
            match = parser.OFPMatch(
                in_port=in_port,
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=ip_src,
                ipv4_dst=ip_dst,
                tcp_dst=tcp_port if tcp_port else 0
            )
            self.add_flow(datapath, 2, match, actions)
        return actions

    def setup_exam_flows(self, datapath, in_port, ip_src, ip_dst):
        # Drop student traffic, allow researcher traffic
        if ip_src not in self.student_ips:
            return self.setup_normal_flows(datapath, in_port, ip_src, ip_dst)
        return []

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip = pkt.get_protocol(ipv4.ipv4)
            tcp_pkt = pkt.get_protocol(tcp.tcp)
            tcp_port = tcp_pkt.dst_port if tcp_pkt else None
            
            actions = []
            if self.exam_mode and self.simulation_mode:
                actions = self.setup_exam_simulation_flows(datapath, in_port, ip.src, ip.dst, tcp_port)
            elif self.simulation_mode:
                actions = self.setup_simulation_flows(datapath, in_port, ip.src, ip.dst, tcp_port)
            elif self.exam_mode:
                actions = self.setup_exam_flows(datapath, in_port, ip.src, ip.dst)
            else:
                actions = self.setup_normal_flows(datapath, in_port, ip.src, ip.dst)

            if actions:
                self._send_package(msg, datapath, in_port, actions)
