from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp

class NetworkSlicingController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(NetworkSlicingController, self).__init__(*args, **kwargs)
        self.slice_to_port = {
            # Traffic rules for S1
            1: {1: 3, 2: 5, 3: 1, 5: 2},  # Ports for student and researcher traffic
            2: {1: 2, 2: 1},              # Traffic between S1 and S3
            3: {1: 4, 2: 3, 4: 1, 3: 2},  # Ports for S3 handling both slices
            4: {1: 2, 2: 1}               # Traffic between S1 and S4
        }

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Table-miss flow entry
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == 0x0806:  # ARP handling
            self.logger.info("Handling ARP packet on Switch %s", dpid)

        # Lookup output port
        if dpid in self.slice_to_port and in_port in self.slice_to_port[dpid]:
            out_port = self.slice_to_port[dpid][in_port]
        else:
            out_port = ofproto.OFPP_FLOOD  # Default to flooding if no match

        actions = [parser.OFPActionOutput(out_port)]

        # Install flow rule for future packets
        match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst)
        self.add_flow(datapath, 1, match, actions)

        # Forward the current packet
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data,
        )
        datapath.send_msg(out)
