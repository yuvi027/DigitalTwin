from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response
import json

# REST API paths
BASE_URL = "/slicing"
NETWORK_SLICE_INSTANCE = "network_slice_instance"

class NetworkSlicingController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exam = False
        self.simulation = False

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install default flow to avoid packet-in flood
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
        )
        datapath.send_msg(mod)

    def remove_flows(self, datapath):
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        mod = parser.OFPFlowMod(datapath=datapath, command=parser.OFPFC_DELETE, out_port=parser.OFPP_ANY, out_group=parser.OFPG_ANY, match=match)
        datapath.send_msg(mod)

    def configure_slice(self, datapath, exam, simulation):
        """Reconfigures flow rules based on exam and simulation states."""
        self.remove_flows(datapath)  # Remove all previous flows
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        if not exam and not simulation:
            # Default: researcher traffic (R) -> s1-s3-s4, student traffic (S) -> s1-s2-s4
            match_r = parser.OFPMatch(eth_src="00:00:00:00:00:03")  # Match researcher traffic
            actions_r = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 1, match_r, actions_r)
        # Implement other use cases similarly...

# REST API Controller
class SlicingRestAPI(ControllerBase):
    def __init__(self, req, link, data, **config):
        super().__init__(req, link, data, **config)
        self.network_slice = data[NETWORK_SLICE_INSTANCE]

    @route("slice", BASE_URL + "/set", methods=["POST"])
    def set_slice(self, req, **kwargs):
        network_slice = self.network_slice
        try:
            params = json.loads(req.body)
            network_slice.exam = params.get("exam", False)
            network_slice.simulation = params.get("simulation", False)
            return Response(status=200, body=json.dumps({"status": "success"}))
        except Exception as e:
            return Response(status=400, body=json.dumps({"error": str(e)}))

