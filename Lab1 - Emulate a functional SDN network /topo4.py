"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        H1 = self.addHost( 'h1' , ip = '10.0.0.1', mac = '00:00:00:00:00:01')
        H2 = self.addHost( 'h2' , ip = '10.0.0.2', mac = '00:00:00:00:00:02')
	H3 = self.addHost( 'h3' , ip = '10.0.0.3', mac = '00:00:00:00:00:03')
	H4 = self.addHost( 'h4' , ip = '10.0.0.4', mac = '00:00:00:00:00:04')	
        S1 = self.addSwitch( 's1' )
        S2 = self.addSwitch( 's2' )
	S3 = self.addSwitch( 's3' )

        # Add links
        self.addLink( S1, S2 )
        self.addLink( S1, S3 )
	self.addLink( S2, S3 )
        self.addLink( H1, S1 )
	self.addLink( H3, S1 )
	self.addLink( H2, S2 )
	self.addLink( H4, S2 )	

topos = { 'mytopo': ( lambda: MyTopo() ) }
