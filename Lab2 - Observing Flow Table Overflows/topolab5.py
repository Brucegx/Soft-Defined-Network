from mininet.topo import Topo
from mininet.link import TCLink
class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        Host1 = self.addHost( 'h1',ip='10.0.0.1')
        Host2 = self.addHost( 'h2',ip='10.0.0.2')
       
        S1 = self.addSwitch( 's1' )
        

        # Add links
        l1=self.addLink( Host1, S1 )
        l2=self.addLink( Host2, S1 )
        

topos = { 'mytopo': ( lambda: MyTopo() ) }
