from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.util import dumpNodeConnections

from subprocess import Popen
from time import sleep
from argparse import ArgumentParser

import os

parser = ArgumentParser(description="Parameters for Setting the Network")

parser.add_argument('--dir', '-d',
                    help="Directory for storing the outputs",
                    required=True)

parser.add_argument('--time', '-t',
                    help="Duration of the experiment (seconds)",
                    type=float,
                    default=10)

parser.add_argument('--maxq',
                    type=int,
                    help="Max buffer size of the network interface (packets)",
                    default=100)

# An RTO (RETRANSMISSION TIMEOUT) occurs when the sender is missing too many acknowledgments and decides to take a
# time out and stop sending altogether.
parser.add_argument('--min_rto',
                    type=float,
                    help="Min RTO (ms)",
                    default=1000)

parser.add_argument('--disable_attacker',
                    type=bool,
                    help="Boolean value to indicate if attacker is disabled",
                    default=False)

parser.add_argument('--cong',
                    help="TCP Congestion Control Algorithm to use",
                    default="reno")

parser.add_argument('--burst_period',
                    type=float,
                    help="Interburst period",
                    default=0.5)

parser.add_argument('--burst_duration',
                    type=float,
                    help="Interburst duration",
                    default=0.15)

# Bandwidths of the server link, attacker link, server link, and bottle-neck link

parser.add_argument('--bw-server', '-bs',
                    type=float,
                    help="Bandwidth of server link (Mb/s)",
                    default=500)

parser.add_argument('--bw-attacker', '-ba',
                    type=float,
                    help="Bandwidth of attacker (network) link (Mb/s)",
                    default=500)

parser.add_argument('--bw-benign', '-bi',
                    type=float,
                    help="Bandwidth of benign (network) link (Mb/s)",
                    default=500)

# Notice Bandwidth of bottleneck link is lower
parser.add_argument('--bw-bottleneck', '-bb',
                    type=float,
                    help="Bandwidth of bottleneck link (Mb/s)",
                    default=1.5)

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    default=2)

# Export parameters
args = parser.parse_args()

class NetworkTopology(Topo):

    def build(self):

        # Two switches
        switch0 = self.addSwitch('switch0')
        switch1 = self.addSwitch('switch1')

        # Three hosts: normal client, attacker client, server
        attacker_client = self.addHost('attacker')
        benign_client = self.addHost('benign')
        server = self.addHost('server')

        # Links

        # Add a link between both clients and switch0.
        # Each client has a bandwidth of 500Mb/s
        # Link propagation delay of 2ms

        self.addLink(attacker_client, switch0, bw=args.bw_attacker, delay=args.delay)
        self.addLink(benign_client, switch0, bw=args.bw_benign, delay=args.delay)

        # Add a link between both switches, this is the bottleneck link.
        # Bandwidth 1.5 Mb/s
        # Max buffer size of 500 packets
        # Link propagation delay of 2ms
        self.addLink(switch0, switch1, bw=args.bw_bottleneck, max_queue_size=args.maxq, delay=args.delay)

        # Add link between switch1 and server
        # The server has a bandwidth of 500Mb/s
        # Link propagation delay of 2ms
        self.addLink(server, switch1, bw=args.bw_server, delay=args.delay)

        return


def start_iperf(net):

    # iPerf is a widely used tool for network performance measurement and tuning.
    # Our server will be running iperf

    print("Starting the iperf server.")

    server = net.get('server')
    server.popen("iperf -s -w 16m >> %s/iperf_server.txt" % args.dir, shell=True)

    client = net.get('benign')
    cmd = "ip route change 10.0.0.0/8 dev benign-eth0  proto kernel  scope link  src %s rto_min 1000" % client.IP()
    client.popen(cmd, shell=True).communicate()
    client.popen("iperf -c %s -t %f -i %f -l %f > %s/iperf_out.txt" % (server.IP(), args.time, 2, 32768, args.dir),
                 shell=True)

def start_attacker(net):
    client = net.get('attacker')
    server = net.get('server')
    print("Burst period:", args.burst_period)
    # Attacker client will perform the shrew attack in bursts by calling the shrew.py script
    client.popen("python shrew.py %s %f %f %f" % (server.IP(), args.burst_period, args.burst_duration, args.time))

def topology():

    # Create directory if it doesn't exist
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    # Set the TCP Congestion Control Algorithm
    os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)

    os.system("sysctl net.ipv4.tcp_frto=0")

    # Create the Mininet Network Topology and start the network
    topo = NetworkTopology()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()

    # This dumps the topology and how nodes are interconnected through
    # links.
    dumpNodeConnections(net.hosts)

    # Start the iperf server
    start_iperf(net)

    # Start the attacker
    if not args.disable_attacker:
        print("Starting the attacker.")
        start_attacker(net)

    # Sleep for + 5 to give iperf chance to finish up
    sleep(args.time + 5)
    net.stop()

    # Ensure that all processes you create within Mininet are killed.
    # Sometimes they require manual killing.
    Popen("pgrep -f ping | xargs kill -9", shell=True).wait()
    Popen("pgrep -f iperf | xargs kill -9", shell=True).wait()
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()


if __name__ == '__main__':
    topology()