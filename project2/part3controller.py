# Part 3 of UWCSE's Project 3
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

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

class Part3Controller (object):
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
    msg = of.ofp_flow_mod()
    msg.priority = 1
    msg.match.dl_type = 0x0800
    msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
    self.connection.send(msg)

    msg.priority = 2
    msg.match.dl_type = 0x0806
    msg.match.nw_proto = None
    self.connection.send(msg)

    # block all ICMP traffic from untrusted host
    notrust_rule = of.ofp_flow_mod()
    notrust_rule.priority = 5
    notrust_rule.match.dl_type = 0x0800
    notrust_rule.match.nw_proto = 1
    notrust_rule.match.nw_src = IPAddr((IPS["hnotrust"])[0])
    self.connection.send(notrust_rule)   
  
  def core_rule_setup(self, host, n):
    core_rule = of.ofp_flow_mod()
    core_rule.priority = n
    core_rule.match.nw_dst = IPAddr((IPS[host])[0])
    core_rule.actions = {of.ofp_action_output(port = n)}
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

    """core used for routing only
    core_rule_ip = of.ofp_flow_mod()
    core_rule_ip.priority = 11
    core_rule_ip.match.dl_type = 0x0800
    core_rule_ip.match.nw_proto = 1
    core_rule_ip.match.nw_dst = IPAddr((IPS["h10"])[0])
    core_rule_ip.actions = {of.ofp_action_output(port = 1)}
    self.connection.send(core_rule_ip)

    core_rule_ip.priority = 10
    core_rule_ip.match.nw_dst = IPAddr((IPS["h20"])[0])
    core_rule_ip.actions = {of.ofp_action_output(port = 2)}
    self.connection.send(core_rule_ip)

    core_rule_ip.priority = 9
    core_rule_ip.match.nw_dst = IPAddr((IPS["h30"])[0])
    core_rule_ip.actions = {of.ofp_action_output(port = 3)}
    self.connection.send(core_rule_ip)
    
    core_rule_ip.priority = 8
    core_rule_ip.match.nw_dst = IPAddr((IPS["serv1"])[0])
    core_rule_ip.actions = {of.ofp_action_output(port = 4)}
    self.connection.send(core_rule_ip)
    
    core_rule_ip.priority = 7
    core_rule_ip.match.nw_dst = IPAddr((IPS["hnotrust"])[0])
    core_rule_ip.actions = {of.ofp_action_output(port = 5)}
    self.connection.send(core_rule_ip)

    core_rule_arp = of.ofp_flow_mod()
    core_rule_arp.priority = 6
    core_rule_arp.match.dl_type = 0x0806
    core_rule_arp.match.nw_dst = IPAddr((IPS["h10"])[0])
    core_rule_arp.actions = {of.ofp_action_output(port = 1)}
    self.connection.send(core_rule_arp)

    core_rule_arp.priority = 5
    core_rule_arp.match.nw_dst = IPAddr((IPS["h20"])[0])
    core_rule_arp.actions = {of.ofp_action_output(port = 2)}
    self.connection.send(core_rule_arp)

    core_rule_arp.priority = 4
    core_rule_arp.match.nw_dst = IPAddr((IPS["h30"])[0])
    core_rule_arp.actions = {of.ofp_action_output(port = 3)}
    self.connection.send(core_rule_arp)
    
    core_rule_arp.priority = 3
    core_rule_arp.match.nw_dst = IPAddr((IPS["serv1"])[0])
    core_rule_arp.actions = {of.ofp_action_output(port = 4)}
    self.connection.send(core_rule_arp)
    
    core_rule_arp.priority = 2
    core_rule_arp.match.nw_dst = IPAddr((IPS["hnotrust"])[0])
    core_rule_arp.actions = {of.ofp_action_output(port = 5)}
    self.connection.send(core_rule_arp)"""

    self.core_rule_setup("h10", 1)
    self.core_rule_setup("h20", 2)
    self.core_rule_setup("h30", 3)
    self.core_rule_setup("serv1", 4)
    self.core_rule_setup("hnotrust", 5)


  def dcs31_setup(self):
    #put datacenter switch rules here
    self.norm_switch_setup()
    
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
    print ("Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump())

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Part3Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
