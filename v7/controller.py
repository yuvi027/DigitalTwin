import threading
from time import sleep
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp
from multiprocessing import Process


class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)

        self.current_slice = "normal"
        self.simulation_port = 5000

        # out_port = slice_to_port[dpid][in_port]
        self.slice_to_port = {
            1: {1: 3, 3: 1, 2: 4, 4: 2},
            4: {1: 3, 3: 1, 2: 4, 4: 2},
            2: {1: 2, 2: 1},
            3: {1: 2, 2: 1},
        }


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
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
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match["in_port"]
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        ip = pkt.get_protocol(ipv4.ipv4)
        if not ip:
            return

        src_ip = ip.src
        dst_ip = ip.dst

        if dpid == 1:
            if src_ip == "10.0.0.1" and dst_ip == "10.0.0.2":
                match = datapath.ofproto_parser.OFPMatch(in_port=in_port, ipv4_src=src_ip, ipv4_dst=dst_ip)
                actions = [datapath.ofproto_parser.OFPActionSetQueue(123)]
                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)
            
            if src_ip == "10.0.0.3" and dst_ip == "10.0.0.4":
                match = datapath.ofproto_parser.OFPMatch(in_port=in_port, ipv4_src=src_ip, ipv4_dst=dst_ip)
                actions = [datapath.ofproto_parser.OFPActionSetQueue(234)]
                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)

# Switch 2
        elif dpid == 2:
            if in_port == 1:
                out_port = 2
            else:
                out_port = 1

            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)
        
# Switch 3
        elif dpid == 3:
            if in_port == 1:
                out_port = 2
            else:
                out_port = 1

            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)
        

        elif dpid == 4:
            if src_ip == "10.0.0.1" and dst_ip == "10.0.0.2":
                out_port = 3
            
            elif src_ip == "10.0.0.3" and dst_ip == "10.0.0.4":
                out_port = 4
            
            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)



        #out_port = self.slice_to_port[dpid][in_port]
        #actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #match = datapath.ofproto_parser.OFPMatch(in_port=in_port)

        #self.add_flow(datapath, 1, match, actions)
        #self._send_package(msg, datapath, in_port, actions)
