# Part 3 of UWCSE's Project 3
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
from pox.lib.packet import arp
from pox.lib.packet import ethernet

log = core.getLogger()

#statically allocate a routing table for hosts
#MACs used in only in part 4
IPS = {
  "h10" : ("10.0.1.10", '00:00:00:00:00:01'),
  "h20" : ("10.0.2.20", '00:00:00:00:00:02'),
  "h30" : ("10.0.3.30", '00:00:00:00:00:03'),
  "serv1" : ("10.0.4.10", '00:00:00:00:00:04'),
  "hnotrust" : ("172.16.10.100", '00:00:00:00:00:05'),
}

ips_seen = set() # set of ips seen for core switch

class Part4Controller (object):
  """
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    print (connection.dpid)
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)
    #use the dpid to figure out what switch is being created
    if (connection.dpid == 1):
      self.s1_setup()
    elif (connection.dpid == 2):
      self.s2_setup()
    elif (connection.dpid == 3):
      self.s3_setup()
    elif (connection.dpid == 21):
      self.cores21_setup()
    elif (connection.dpid == 31):
      self.dcs31_setup()
    else:
      print ("UNKNOWN SWITCH")
      exit(1)
  
  def norm_switch_setup(self):
    # flood all ip and arp packets
    msg = of.ofp_flow_mod()
    msg.priority = 1
    msg.match.dl_type = 0x0800
    msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
    self.connection.send(msg)

    msg.priority = 2
    msg.match.dl_type = 0x0806
    msg.match.nw_proto = None
    self.connection.send(msg)
    
    # drop all icmp packets from hnotrust
    notrust_rule = of.ofp_flow_mod()
    notrust_rule.priority = 5
    notrust_rule.match.dl_type = 0x0800
    notrust_rule.match.nw_proto = 1
    notrust_rule.match.nw_src = IPAddr((IPS["hnotrust"])[0])
    self.connection.send(notrust_rule) 

  def core_rule_setup(self, host, n):
    # forwards all ip and arp packets destined to 'host' on port 'n' 
    core_rule = of.ofp_flow_mod()
    core_rule.priority = n
    core_rule.match.nw_dst = IPAddr((IPS[host])[0])
    core_rule.actions = [of.ofp_action_output(port = n)]
    core_rule.match.dl_type = 0x0806
    self.connection.send(core_rule)
        
    core_rule.priority = n + 5
    core_rule.match.dl_type = 0x0800
    self.connection.send(core_rule)

  def s1_setup(self):
    #put switch 1 rules here
    self.norm_switch_setup()
    
  def s2_setup(self):
    #put switch 2 rules here
    self.norm_switch_setup()

  def s3_setup(self):
    #put switch 3 rules here
    self.norm_switch_setup()

  def cores21_setup(self):
    #put core switch rules here
    pass

  def dcs31_setup(self):
    #put datacenter switch rules here
    self.norm_switch_setup()
    
    # drop all ip packets from hnotrust
    notrust_rule = of.ofp_flow_mod()
    notrust_rule.priority = 4
    notrust_rule.match.dl_type = 0x0800
    notrust_rule.match.nw_src = IPAddr((IPS["hnotrust"])[0])
    self.connection.send(notrust_rule)

  #used in part 4 to handle individual ARP packets
  #not needed for part 3 (USE RULES!)
  #causes the switch to output packet_in on out_port
  def resend_packet(self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
    self.connection.send(msg)

  def _handle_PacketIn (self, event):
    """
    Packets not handled by the router rules will be
    forwarded to this method to be handled by the controller
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.


    # should only be triggered on the core switch as other switches
    # already have a rule to flood ARP packets
    if packet.type == packet.ARP_TYPE:
        arp_packet = packet.find('arp')
        mac_addr_src = packet.src
        ip_addr_src = arp_packet.protosrc
        src_port = packet_in.in_port
        if not ip_addr_src in ips_seen:
            core_rule = of.ofp_flow_mod()
            core_rule.priority = len(ips_seen) * 2 + 1
            core_rule.match.nw_dst = IPAddr(ip_addr_src)
            # rule edits header of incoming packets to the correct MAC addr
            # and routes them to correct port
            core_rule.actions.append(of.ofp_action_dl_addr.set_dst(EthAddr(mac_addr_src)))
            core_rule.actions.append(of.ofp_action_output(port = src_port))
            core_rule.match.dl_type = 0x0806
            self.connection.send(core_rule)
        
            core_rule.priority = len(ips_seen) * 2 + 2
            core_rule.match.dl_dst = None
            core_rule.match.dl_type = 0x0800
            self.connection.send(core_rule)
            
            ips_seen.add(ip_addr_src)
        
        # reply to ARP messages with arbitrary MAC addr to assume control
        arp_reply = arp()
        arp_reply.hwsrc = EthAddr("de:ed:be:ef:ca:fe")
      	arp_reply.hwdst = packet.src
      	arp_reply.opcode = arp.REPLY
        arp_reply.protosrc = arp_packet.protodst
      	arp_reply.protodst = packet.payload.protosrc
      	ether = ethernet()
      	ether.type = ethernet.ARP_TYPE
      	ether.dst = packet.src
        ether.src = EthAddr("de:ad:be:ef:ca:fe")
      	ether.payload = arp_reply                                                
        self.resend_packet(ether, src_port)

    else: # if packet isn't an ARP packet do nothing
        print ("Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump())

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Part4Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
