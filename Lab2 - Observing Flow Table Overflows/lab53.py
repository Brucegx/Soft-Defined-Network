
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
	    self.arp_table={}
        self.arp_table["10.0.0.1"] = "00:00:00:00:00:01"
        self.arp_table["10.0.0.2"] = "00:00:00:00:00:02"

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Insert Static rule
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
	#dpid = datapath.id  # classifying the switch ID

        """ 
        Call back method for PacketIn Message
        This is the call back method when a PacketIn Msg is sent
        from a switch to the controller
        It handles L3 classification in this function:
    	""" 

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ethertype = eth.ethertype
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
	    ipv4_src = eth.src
	    ipv4_dst = eth.dst#what I changed for defining the srcip&dstip

        # process ARP 
        if ethertype == ether.ETH_TYPE_ARP:
            self.handle_arp(datapath, in_port, pkt)
            return

        match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                ip_proto = inet.IPPROTO_TCP,
                                ipv4_dst = "10.0.0.1",
                                ipv4_src = "10.0.0.2",
                                src_port = tcp_pkt.src_port,
                                dst_port = dcp_pkt.dst_port)#there may not be right
        actions = [parser.OFPActionOutput(2)]
        self.add_flow(datapath, 10, match, actions)

        match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                ip_proto = inet.IPPROTO_TCP,
                                ipv4_dst = "10.0.0.2",
                                ipv4_src = "10.0.0.1",
                                src_port = tcp_pkt.src_port,
                                dst_port = dcp_pkt.dst_port)
        actions = [parser.OFPActionOutput(1)]
        self.add_flow(datapath, 10, match, actions)

    # Member methods you can call to install TCP/UDP/ICMP fwding rules
    #@handle_ip(datapath, in_port, pkt)
    def add_layer4_rules(self, datapath, ipv4_src, ipv4_dst, ip_proto, src_port, dst_port):#uncompleted
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(fwd_port)]
        match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                ip_proto = ip_proto,
                                ipv4_dst = ipv4_dst)
        self.add_flow(datapath, priority, match, actions)

    # Member methods you can call to install general rules
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    def handle_arp(self, datapath, in_port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # parse out the ethernet and arp packet
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        # obtain the MAC of dst IP  
        arp_resolv_mac = self.arp_table[arp_pkt.dst_ip]

        ### generate the ARP reply msg, please refer RYU documentation
        ### the packet library section
	ether_hd = ethernet.ethernet(dst = eth_pkt.src, 
                                src = arp_resolv_mac, 
                                ethertype = ether.ETH_TYPE_ARP);
        arp_hd = arp.arp(hwtype=1, proto = 2048, hlen = 6, plen = 4,
                         opcode = 2, src_mac = arp_resolv_mac, 
                         src_ip = arp_pkt.dst_ip, dst_mac = eth_pkt.src,
                         dst_ip = arp_pkt.src_ip);
        arp_reply = packet.Packet()
        arp_reply.add_protocol(ether_hd)
        arp_reply.add_protocol(arp_hd)
	arp_reply.serialize()
       
        actions = [parser.OFPActionOutput(in_port)];
        out = parser.OFPPacketOut(datapath, ofproto.OFP_NO_BUFFER, 
                                  ofproto.OFPP_CONTROLLER, actions,
                                  arp_reply.data)
        datapath.send_msg(out)

