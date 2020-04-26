from collections import Counter
from datetime import datetime, date
import json
from  multiprocessing import Process
import os
import sys

import folium
from folium.plugins import HeatMap
from geoip2 import database

import matplotlib.pyplot as plt

from matplotlib.dates import date2num
import pandas as pd
import zmq

from scapy.all import *


def plot_ts(ts_data, title, color):
    dates = date2num(ts_data)
    plt.style.use('dark_background')
    plt.plot_date(
        dates, [1]*len(dates), marker = "|", 
        markersize = 150, color = color)
    plt.ylim(0.97,1.2)
    plt.title(title)
    plt.yticks([])

    plt.show()
    # * I know this is cheating. But seems to be the only way.


def query_geoip(ip_list):
    resolved_src_country = []
    resolved_locale = []

    for each_ip in ip_list:
        try:
            result = reader.city(each_ip)
            resolved_src_country.append(
                                  result.country.iso_code)
            # This returns the ISO 3166 alpha 2 code.
            resolved_locale.append([result.location.latitude, 
                                    result.location.longitude])
            # Each location is returned as array. This is 
            # done so that this data can be directly fed to 
            # HeatMap function later.
        except:
            continue    # Skip private IPs

    return resolved_src_country, resolved_locale


def obtain_geoip_info(src_ip_list, dst_ip_list):
    resolved_src_country = []
    resolved_dst_country = []
    src_location = []
    dst_location = []
    unique_src_country = {}
    unique_dst_country = {}

    resolved_src_country, src_locale = query_geoip(src_ip_list)
    resolved_dst_country, dst_locale  = query_geoip(dst_ip_list)

    unique_src_country = set(resolved_src_country)
    unique_dst_country = set(resolved_dst_country)

    print('\nUnique Source Countries are ')
    print(unique_src_country)
    print('Unique Destination Countries are ')
    print(unique_dst_country)

    return (resolved_src_country, src_locale, 
            resolved_dst_country, dst_locale)


def generate_choropleth(src_country, title):
    country_counter = dict(Counter(src_country))

    geo_ip_data = pd.DataFrame(list(
                            country_counter.items()),
                            columns = ['Country', 'Count'])

    choro_map = folium.Map(tiles = "cartodbdark_matter", 
                           location = [32.635588, 4.879570], 
                           zoom_start = 2.4)
    try:
        folium.Choropleth(
                    geo_data = GEO_JSON,
                    name = 'choropleth',
                    data = geo_ip_data,
                    columns = ['Country', 'Count'],
                    key_on = 'feature.properties.iso_a2',
                    fill_color = "Purples",
                    fill_opacity = 0.9,
                    line_opacity = 0.3,
                    nan_fill_color = '#110c11',
                    nan_fill_opacity = 0.4,
                    legend_name = title
                    ).add_to(choro_map)
        folium.LayerControl().add_to(choro_map)
        choro_map.save('Choropleth-{}.html'.format(title))

    except FileNotFoundError:
        print('GeoJSON File not found!!\n'
              'Choropleth is not plotted...')


def generate_heatmap(src_locale, title):
    heat_map = folium.Map(tiles = "cartodbdark_matter", 
                          location = [32.635588, 4.879570], 
                          zoom_start = 2.4)

    HeatMap(src_locale).add_to(heat_map)
    heat_map.save('HeatMap-{}.html'.format(title))


def generate_packet_size_plot(packets):
    ts_list = []
    packet_size = []

    for pkt in packets:
        if pkt.haslayer(IP):
            packet_size.append((pkt[IP].len))
            packet_ts = datetime.fromtimestamp(pkt.time)
            ts_list.append(packet_ts)

    plt.style.use('dark_background')
    plt.ylabel('Bytes')
    plt.title('IP Packet Size Flow')
    plt.ylim(0,2000)
    plt.fill_between(ts_list, payload_size, color="#6f00ff", alpha=0.4)
    plt.show()
    

def matcher(source_set, blacklist_set):
    match_list = []

    for each_candidate in source_set:
        if each_candidate in blacklist_set:
            match_list.append(each_candidate)
    return match_list


def threat_intel(src_ip_set, dst_ip_set, domain_set):
    blacklist_ip_count = 0
    blacklist_ad_domain_count = 0
    blacklist_trackers_count = 0
    blacklist_coin_miner_count = 0
    blacklist_corona_count = 0

    try:
        blacklist_ip_set = set(
                            map(str.strip, open(
                                            BLACKLIST_IP_DB)))
        blacklist_ad_domain_set = set(
                            map(str.strip, open(
                                            BLACKLIST_AD_DB)))
        blacklist_tracker_set = set(
                            map(str.strip, open(
                                            BLACKLIST_TRACKER_DB)))
        blacklist_coin_miner_set = set(
                            map(str.strip, open(
                                            BLACKLIST_COINMINER_DB)))
        blacklist_covid_domain_set = set(
                            map(str.strip, open(
                                            BLACKLIST_COVID_DOMAIN_DB)))
        
        blacklist_src_ip = matcher(
                            src_ip_set, blacklist_ip_set)
        blacklist_dst_ip = matcher(
                                dst_ip_set, blacklist_ip_set)    
        blacklist_ad_domain = matcher(
                                domain_set, blacklist_ad_domain_set)
        blacklist_tracker = matcher(
                                domain_set, blacklist_tracker_set)
        blacklist_coin_miner = matcher(
                                domain_set, blacklist_coin_miner_set)
        blacklist_covid_domain = matcher(
                                domain_set, blacklist_covid_domain_set)

        print('Blacklisted Source IP match -> ' 
                        + str(len(blacklist_src_ip)))
        if len(blacklist_src_ip) != 0:
            print(blacklist_src_ip)

        print('Blacklisted Destination IP match -> ' 
                        + str(len(blacklist_dst_ip)))
        if len(blacklist_dst_ip) != 0:
            print(blacklist_dst_ip)

        print('Blacklisted Ad Server Domain match -> '
                        + str(len(blacklist_ad_domain)))
        if len(blacklist_dst_ip) != 0:
            print(blacklist_ad_domain)

        print('Blacklisted Agressive Trackers Domain match -> '
                        + str(len(blacklist_tracker)))
        if len(blacklist_tracker) != 0:
            print(blacklist_tracker)

        print('Blacklisted Coin Miner Domain match -> ' 
                        + str(len(blacklist_coin_miner)))
        if len(blacklist_coin_miner) != 0:
            print(blacklist_coin_miner)

        print('Blacklisted COVID-19 Phising Domain match -> ' 
                        + str(len(blacklist_covid_domain)))
        if len(blacklist_covid_domain) != 0:
            print(blacklist_covid_domain)


    except FileNotFoundError:
        print('One of the Threat Intel Files doesnot exist!!\n'
              'Threat Intel process is skipped...')


def dns_report():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:7777")
    socket.setsockopt(zmq.SUBSCRIBE, b'packets')

    # Second, synchronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect('tcp://localhost:6666')

    # send a synchronization request
    syncclient.send(b'')

    # wait for synchronization reply
    syncclient.recv()

    topic = socket.recv_string()
    packets = socket.recv_pyobj()

    query_count = 0
    dns_req_ts = []
    dns_query = []

    for packet in packets:
        if packet.haslayer(DNSRR):
            # Filtering packets with a DNS Round Robin layer. 
            if isinstance(packet.an, DNSRR):
                query_count += 1
                packet_ts = datetime.fromtimestamp(packet.time)
                dns_req_ts.append(packet_ts)
                # print(packet.an.rrname.decode().strip('.'))
                dns_query.append(packet.an.rrname.decode().strip('.'))
                # Converting to unicode and stripping the root '.'

    print('\nTotal number of DNS Queries made is '
                                     + str(query_count) + '\n')

    # plot_ts(dns_req_ts, 'DNS Flow', '#4d4dff')
    # return dns_query


def arp_report():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:7777")
    socket.setsockopt(zmq.SUBSCRIBE, b'packets')

    # Second, synchronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect('tcp://localhost:6666')

    # send a synchronization request
    syncclient.send(b'')

    # wait for synchronization reply
    syncclient.recv()

    topic = socket.recv_string()
    packets = socket.recv_pyobj()

    arp_count = 0
    src_arp_mac = []
    src_arp_ip = []
    req_arp_ip = []
    req_arp_ts = []
    unique_src_arp_mac = {}
    unique_src_arp_ip = {}
    unique_req_arp_ip = {}

    for packet in packets:
        if packet.haslayer(ARP):
            arp_count += 1
            if packet[ARP].op == 1:  # ARP Request
                src_arp_mac.append(packet[ARP].hwsrc)
                src_arp_ip.append(packet[ARP].psrc)
                req_arp_ip.append(packet[ARP].pdst)
                packet_ts = datetime.fromtimestamp(packet.time)
                req_arp_ts.append(packet_ts)

    unique_src_arp_mac = set(src_arp_mac)
    unique_src_arp_ip = set(src_arp_ip)
    unique_req_arp_ip = set(req_arp_ip)
    req_arp_ip_dist = Counter(req_arp_ip)
    src_arp_ip_dist = Counter(src_arp_ip)
    src_arp_mac_dist = Counter(src_arp_mac)
    print(req_arp_ip_dist)
    print(src_arp_ip_dist)
    print(src_arp_mac_dist)
    print(req_arp_ts)
    
    # plot_ts(req_arp_ts, 'ARP Flow', "#c71585")


def ip_report():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:7777")
    socket.setsockopt(zmq.SUBSCRIBE, b'packets')

    # Second, synchronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect('tcp://localhost:6666')

    # send a synchronization request
    syncclient.send(b'')

    # wait for synchronization reply
    syncclient.recv()

    topic = socket.recv_string()
    packets = socket.recv_pyobj()

    ip_ts = []
    src_ip = []
    dst_ip = []
    unique_src_ip = []
    unique_dst_ip = []
    unique_src_ip_count = 0
    unique_dst_ip_count = 0
    
    for packet in packets:
        if packet.haslayer(IP):
            src_ip.append(packet[IP].src)
            dst_ip.append(packet[IP].dst)
            packet_ts = datetime.fromtimestamp(packet.time)
            ip_ts.append(packet_ts)

    unique_src_ip = set(src_ip)
    unique_dst_ip = set(dst_ip)

    print('\nV----- Unique Source IPs -----V\n')
    print(unique_src_ip)
    print('\nV----- Unique Destination IPs -----V\n')
    print(unique_dst_ip)
    unique_src_ip_count = len(unique_src_ip)
    unique_dst_ip_count = len(unique_dst_ip)

    print('The number of unique source ips is ' 
                    + str(unique_src_ip_count) + '\n')
    print('The number of unique destination ips is ' 
                    + str(unique_dst_ip_count) + '\n')

    
    # (src_country, src_locale, 
    # dst_country, dst_locale) = obtain_geoip_info(src_ip, dst_ip)
    # plot_ts(ip_ts, 'IP Flow', '#af4bce')

    # generate_choropleth(src_country, 'Source Countries')
    # generate_choropleth(dst_country, 'Destination Countries')
    
    # generate_heatmap(src_locale, 'Source Countries')
    # generate_heatmap(dst_locale, 'Destination Countries') 
    # TODO Multiprocess maps creation.
    # return unique_src_ip, unique_dst_ip


def transport_report():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:7777")
    socket.setsockopt(zmq.SUBSCRIBE, b'packets')

    # Second, synchronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect('tcp://localhost:6666')

    # send a synchronization request
    syncclient.send(b'')

    # wait for synchronization reply
    syncclient.recv()

    topic = socket.recv_string()
    packets = socket.recv_pyobj()

    tcp_src_port = []
    tcp_dst_port = []
    udp_src_port = []
    udp_dst_port = []
    tcp_ts = []
    udp_ts = []
    unique_tcp_src_port = {}
    unique_tcp_dst_port = {}
    unique_udp_src_port = {}
    unique_udp_dst_port = {}
    tcp_src_port_count = 0
    tcp_dst_port_count = 0
    udp_src_port_count = 0
    udp_dst_port_count = 0
    tcp_count = 0
    udp_count = 0

    for packet in packets:
        if packet.haslayer(TCP):
            tcp_count += 1
            tcp_src_port.append(packet[IP].sport)
            tcp_dst_port.append(packet[IP].dport)
            packet_ts = datetime.fromtimestamp(packet.time)
            tcp_ts.append(packet_ts)

        elif packet.haslayer(UDP):
            udp_count += 1
            udp_src_port.append(packet[IP].sport)
            udp_dst_port.append(packet[IP].dport)
            packet_ts = datetime.fromtimestamp(packet.time)
            udp_ts.append(packet_ts)

    unique_tcp_src_port = set(tcp_src_port)
    unique_tcp_dst_port = set(tcp_dst_port)
    unique_udp_src_port = set(udp_src_port)
    unique_udp_dst_port = set(udp_dst_port)

    tcp_src_port_count = len(unique_tcp_src_port)
    tcp_dst_port_count = len(unique_tcp_dst_port)
    udp_src_port_count = len(unique_udp_src_port)
    udp_dst_port_count = len(unique_udp_dst_port)

    print('Total TCP packet count is ' + str(tcp_count) + '\n')
    print('V----- Unique TCP Source Ports -----V\n')
    print(unique_tcp_src_port)
    print('\nV----- Unique TCP Destination Ports -----V\n')
    print(unique_tcp_dst_port)
    
    print('\nTotal UDP packet count is ' + str(udp_count) + '\n')
    print('V----- Unique UDP Source Ports -----V\n')
    print(unique_udp_src_port)
    print('\nV----- Unique UDP Destination Ports -----V\n')
    print(unique_udp_dst_port,'\n')

    # plot_ts(tcp_ts, 'TCP Flow', '#bf00ff')
    # plot_ts(udp_ts, 'UDP Flow' , '#6f00ff')


def pcap_reader():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    # set SNDHWM, so we don't drop messages for slow subscribers
    publisher.sndhwm = 1100000
    publisher.bind("tcp://*:7777")  # * 7xxx are data channels.

    # Socket to receive signals
    syncservice = context.socket(zmq.REP)
    syncservice.bind('tcp://*:6666')  # * 6xxx are sync channels.
    # Get synchronization from subscribers

    SUBSCRIBERS_EXPECTED = 5
    subscribers = 0
    while subscribers < SUBSCRIBERS_EXPECTED:
        # wait for synchronization request
        msg = syncservice.recv()
        # send synchronization reply
        syncservice.send(b'')
        subscribers += 1
        print("+1 subscriber (%i/%i)" % (subscribers, SUBSCRIBERS_EXPECTED))

    try:
        packets = rdpcap(input_pcap_file)
    except FileNotFoundError:
        packets = None

    i = 0
    topic = 'packets'
    while i < 1:
        i += 1
        publisher.send_string(topic, zmq.SNDMORE)
        publisher.send_pyobj(packets)
        print('Sent Packets to Plugins')
    

def generate_summary():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:7777")
    socket.setsockopt(zmq.SUBSCRIBE, b'packets')

    # Second, synchronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect('tcp://localhost:6666')

    # send a synchronization request
    syncclient.send(b'')

    # wait for synchronization reply
    syncclient.recv()

    topic = socket.recv_string()
    packets = socket.recv_pyobj()

    if packets is None:
        print('Input pcap file does not exist!!\n'
              'Exiting...')
        exit()

    with open(output_summary_file, 'w') as fp:
        try:
            original_stdout = sys.stdout
            sys.stdout = fp
            fp.write(packets.summary(       
                        prn=lambda x: str(x.time) 
                                       + ' ' + x.summary()))
            # Modifying lambda function as it didn't return packet time.
        except TypeError as e:
            sys.stdout = original_stdout
    
    packet_count = len(packets)
    print('\nThe numbers of packets in this pcap file is '
                                 + str(packet_count) + '\n')
    print('####### Summary of packets has been successfuly written in {}'
                                  ' #######'.format(output_summary_file))

def main():
    Process(target = pcap_reader).start()
    Process(target = generate_summary).start()
    Process(target = dns_report).start()
    Process(target = arp_report).start()
    Process(target = ip_report).start()
    Process(target = transport_report).start()
    Process(target = threat_intel).start()

    # # generate_packet_size_plot(packets)    

if len(sys.argv) not in [3, 4]:
    print('''

**** Usage: python3 myra.py <pcap_file> <summary_output_file> ****
            
        ''')
    exit()

script_name = sys.argv[0]
input_pcap_file = sys.argv[1]
output_summary_file = sys.argv[2]

# * For GeoIP2 API
GEOIP_DB = 'Resources/GeoIP/GeoLite2-City.mmdb'

# * GeoJSON File
GEO_JSON = 'Resources/GeoJSON/world_mid_res.json'

# * Threat Intel Feeds
BLACKLIST_IP_DB = 'Resources/Blacklist/blacklist.ip'
BLACKLIST_AD_DB = 'Resources/Blacklist/blacklist.ads'
BLACKLIST_TRACKER_DB = 'Resources/Blacklist/blacklist.trackers'
BLACKLIST_COINMINER_DB = 'Resources/Blacklist/blacklist.coinminer'
BLACKLIST_COVID_DOMAIN_DB = 'Resources/Blacklist/blacklist.corona'

# Creating GeoIP Reader during initialization and using this same object
# across multiple requests as creation of it is expensive.
try:
    reader = database.Reader(GEOIP_DB)
except FileNotFoundError:
    print('The GeoIP DB file does not exist!!i\n'
          'Exiting..')

print('''

    ,·'´¨;.  '                       ,-·-.          ,'´¨;         ,. -  .,                              ,.,   '      
    ;   ';:\           .·´¨';\       ';   ';\      ,'´  ,':\'     ,' ,. -  .,  `' ·,                     ;´   '· .,     
   ;     ';:'\      .'´     ;:'\       ;   ';:\   .'   ,'´::'\'    '; '·~;:::::'`,   ';\                .´  .-,    ';\   
   ;   ,  '·:;  .·´,.´';  ,'::;'       '\   ';::;'´  ,'´::::;'      ;   ,':\::;:´  .·´::\'             /   /:\:';   ;:'\' 
  ;   ;'`.    ¨,.·´::;'  ;:::;          \  '·:'  ,'´:::::;' '      ;  ·'-·'´,.-·'´:::::::';          ,'  ,'::::'\';  ;::'; 
  ;  ';::; \*´\:::::;  ,':::;           '·,   ,'::::::;'´      ;´    ':,´:::::::::::·´'       ,.-·'  '·~^*'´¨,  ';::; 
 ';  ,'::;   \::\;:·';  ;:::; '            ,'  /::::::;'  '       ';  ,    `·:;:-·'´            ':,  ,·:²*´¨¯'`;  ;::'; 
 ;  ';::;     '*´  ;',·':::;            ,´  ';\::::;'  '         ; ,':\'`:·.,  ` ·.,           ,'  / \::::::::';  ;::'; 
 \´¨\::;          \¨\::::;             \`*ª'´\\::/            \·-;::\:::::'`:·-.,';        ,' ,'::::\·²*'´¨¯':,'\:;  
  '\::\;            \:\;·'               '\:::::\';  '            \::\:;'` ·:;:::::\::\'      \`¨\:::/          \::\'  
    '´¨               ¨'                   `*ª'´                 '·-·'       `' · -':::''      '\::\;'            '\;'  '
                                            '                                                 `¨'                   
''')

if __name__ == '__main__':
    main()