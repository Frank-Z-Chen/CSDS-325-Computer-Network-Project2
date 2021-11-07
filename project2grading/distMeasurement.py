"""
This is project2 in CSDS 325 computer network.
This code is to act like trace route. It measure the number of hops, round trip time, and whether ip and port is changed
by the server.
"""

__author__ = "Zhaokuan Chen"
__date__ = "12/1/2020"


import socket
import select
import struct
import time

port = 33434  # port number
ttl = 32      # time to live
header_length = 56  # header length is 56
max_length_of_expected_packet = 1528
# message send to the pinged website
msg = 'measurement for class project. questions to student zxc347@case.edu or professor mxr136@case.edu'
# fill up the payload with 'a'
payload = bytes(msg + 'a' * (1472 - len(msg)), 'ascii')  # fill up the payload with letter 'a'


def main():
    target_list = open('targets.txt', 'r').readlines()  # read targets.txt
    targets = []

    # turn targets.txt to targets array
    for target_name in target_list:
        name_ip_pair = [target_name.strip(), socket.gethostbyname(target_name.strip())]  # make a pair of name and ip
        targets.append(name_ip_pair)  # append the pair so that every input of targets consists of a pair of name and ip

    # trace route every input of targets
    for target in targets:
        # receive socket
        rcv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        rcv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)  # set sockets   !!!!!!consider to revise
        # send socket
        snd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        snd_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)  # set time to live
        snd_socket.sendto(payload, (target[1], port))

        rtt = time.time()  # start counting round trip time
        hop_count = 0
        ip_address_modified = False
        port_modified = False

        while True:
            time_out = False

            select_status = select.select([rcv_socket], [], [], 5)  # timeout=5, in case the packet takes a longer time
            rtt = time.time() - rtt   # stop the timer as soon as receive a packet

            if not select_status[0]:  # probe time out
                time_out = True
                break

            try:
                icmp_packet = rcv_socket.recv(max_length_of_expected_packet)
                icmp_packet_payload_size = len(icmp_packet) - header_length  # the payload size of incoming icmp packet
                ip = '%s.%s.%s.%s' % (str(icmp_packet[12]), str(icmp_packet[13]),   # obtain ip address of icmp packet
                                      str(icmp_packet[14]), str(icmp_packet[15]))
                icmp_port = struct.unpack("!H", icmp_packet[50:52])[0]  # extract the port number from the packet
                hop_count = ttl - icmp_packet[36]  # number of hops

            except socket.error:
                print('cannot extract from socket')

            # if the ip address of icmp packet is not equal to the ip address of the website, then it was modified
            if ip != target[1]:
                ip_address_modified = True
            # if the port number of icmp packet is not equal to 33434, then it was modified
            if icmp_port != port:
                port_modified = True
            # break if anyone equals
            if ip == target[0] or icmp_port == port:
                break

        snd_socket.close()   # close outbound socket
        rcv_socket.close()   # close inbound socket

        if not time_out:
            print('trace route ' + target[0] + ' [' + target[1] + ']')
            print('round trip time: ' + str(rtt * 1000) + 'ms')
            print('number of hops: ' + str(hop_count))
            print('payload size: ' + str(icmp_packet_payload_size))
            print('IP address modified: ' + str(ip_address_modified))
            print('port modified: ' + str(port_modified))
            print('trace route complete moving to next website\r\n')
        else:
            print('trace route time out \r\n')


if __name__ == "__main__":
    main()
