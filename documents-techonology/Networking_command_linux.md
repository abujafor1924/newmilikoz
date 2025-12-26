# **📚 সম্পূর্ণ Ubuntu Network Commands লিস্ট (বাংলায় ব্যাখ্যা সহ)**

## **১. Basic Network Information Commands**

### **১.১ IP Address দেখার জন্য**
```bash
# সব ইন্টারফেসের IP দেখবে (সবচেয়ে কমন)
ip addr show
# বা সংক্ষেপে
ip a

# শুধু IPv4 দেখাবে
hostname -I

# পুরোনো কমান্ড (deprecated কিন্তু অনেক জায়গায় চলে)
ifconfig
```

### **১.২ Network Interfaces দেখার জন্য**
```bash
# সব নেটওয়ার্ক ইন্টারফেসের ডিটেইলস
ip link show

# শুধু Ethernet (LAN) ইন্টারফেস
ip link show eth0

# শুধু WiFi ইন্টারফেস
ip link show wlan0
```

### **১.৩ Public IP দেখার জন্য**
```bash
# ১. curl দিয়ে
curl ifconfig.me

# ২. wget দিয়ে
wget -qO- ifconfig.me

# ৩. dig দিয়ে (ডিএনএস থেকে)
dig +short myip.opendns.com @resolver1.opendns.com
```

---

## **২. Connectivity Testing Commands**

### **২.১ Ping কমান্ড (সবচেয়ে গুরুত্বপূর্ণ)**
```bash
# ১. Google DNS সার্ভারে ping (ইন্টারনেট চেক)
ping 8.8.8.8
# Ctrl+C চাপলে বন্ধ হবে

# ২. নির্দিষ্ট সংখ্যক ping
ping -c 4 google.com
# -c = count (কতবার পিং করবে)

# ৩. Interval পরিবর্তন (সেকেন্ড)
ping -i 2 google.com
# -i = interval (প্রতি ২ সেকেন্ডে পিং করবে)

# ৪. Packet size পরিবর্তন
ping -s 1000 google.com
# -s = size (বাইটে প্যাকেট সাইজ)
```

### **২.২ Traceroute (ডেটার পথ দেখার জন্য)**
```bash
# ১. Basic traceroute
traceroute google.com
# প্রতিটি হপ দেখাবে (রাউটার থেকে রাউটার)

# ২. শুধু TCP ব্যবহার করে
sudo traceroute -T google.com

# ৩. Max hops সেট করা
traceroute -m 30 google.com
# -m = max hops (ডিফল্ট ৩০)

# ৪. Alternative (tracepath)
tracepath google.com
# root permission লাগে না
```

---

## **৩. DNS এবং Network Resolution Commands**

### **৩.১ DNS Lookup**
```bash
# ১. Domain থেকে IP (সবচেয়ে শক্তিশালী)
dig google.com
# ANSWER SECTION দেখবে IP

# ২. শুধু IP দেখাবে
dig +short google.com

# ৩. Reverse DNS lookup (IP থেকে domain)
dig -x 8.8.8.8

# ৪. নির্দিষ্ট DNS server ব্যবহার করে
dig @8.8.8.8 google.com
# @ এর পরে DNS server IP
```

### **৩.২ nslookup (সিম্পল DNS)**
```bash
# ১. Interactive mode
nslookup
> google.com
> exit

# ২. সরাসরি
nslookup google.com

# ৩. নির্দিষ্ট DNS server
nslookup google.com 8.8.8.8
```

### **৩.৩ Host Command**
```bash
# ১. Basic DNS lookup
host google.com

# ২. সব রেকর্ড দেখবে
host -a google.com

# ৩. MX record দেখবে (email server)
host -t MX google.com
```

### **৩.৪ DNS Cache Management**
```bash
# ১. DNS cache flush (systemd)
sudo systemd-resolve --flush-caches

# ২. DNS cache দেখো
sudo systemd-resolve --statistics

# ৩. nmcli দিয়ে (NetworkManager)
sudo nmcli networking off && sudo nmcli networking on
```

---

## **৪. Port এবং Connection Commands**

### **৪.১ Open Ports চেক করা**
```bash
# ১. কোন পোর্ট খোলা আছে (netstat)
sudo netstat -tulpn
# -t = TCP
# -u = UDP
# -l = listening (খোলা পোর্ট)
# -p = process নাম
# -n = numeric (IP, port নাম্বারে)

# ২. ss কমান্ড (netstat এর আধুনিক ভার্সন)
sudo ss -tulpn

# ৩. নির্দিষ্ট পোর্ট চেক
sudo netstat -tulpn | grep :80
# বা
sudo ss -tulpn | grep :80
```

### **৪.২ Network Connections দেখার জন্য**
```bash
# ১. সব active connections
netstat -an

# ২. শুধু ESTABLISHED connections
netstat -an | grep ESTABLISHED

# ৩. Process-wise connections
sudo lsof -i
# -i = internet connections
```

### **৪.৩ Port Scan করা**
```bash
# ১. nmap ইনস্টল (যদি না থাকে)
sudo apt install nmap

# ২. নিজের মেশিন scan
nmap localhost

# ৩. নির্দিষ্ট পোর্ট range
nmap -p 1-1000 localhost

# ৪. অন্য ডিভাইস scan (একই নেটওয়ার্কে)
nmap 192.168.1.1-100
# 192.168.1.1 থেকে 192.168.1.100 পর্যন্ত scan করবে

# ৫. Service version ডিটেক্ট
nmap -sV 192.168.1.1
```

### **৪.৪ Netcat (Network Swiss Army Knife)**
```bash
# ১. Netcat ইনস্টল
sudo apt install netcat

# ২. Port খোলা আছে কিনা চেক
nc -zv google.com 80
# -z = scan mode
# -v = verbose

# ৩. সার্ভার তৈরি (পোর্ট 9999)
nc -l 9999
# -l = listen mode

# ৪. Client হিসেবে কানেক্ট
nc localhost 9999

# ৫. File transfer (সার্ভার)
nc -l 9999 > received_file.txt

# ৬. File transfer (ক্লায়েন্ট)
nc localhost 9999 < file_to_send.txt
```

---

## **৫. Network Configuration Commands**

### **৫.১ IP Address সেট করা**
```bash
# ১. Temporary IP set (রিবুটে চলে যাবে)
sudo ip addr add 192.168.1.100/24 dev eth0
# 192.168.1.100 IP সেট করবে eth0 তে

# ২. IP remove করা
sudo ip addr del 192.168.1.100/24 dev eth0

# ৩. Permanent IP set (netplan দিয়ে)
sudo nano /etc/netplan/01-network-manager-all.yaml
```

**netplan config file:**
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

**অ্যাপ্লাই করতে:**
```bash
sudo netplan apply
```

### **৫.২ Routing Table Commands**
```bash
# ১. Routing table দেখো
ip route show
# বা
route -n

# ২. Default gateway দেখো
ip route | grep default

# ৩. Route add করা
sudo ip route add 10.0.0.0/8 via 192.168.1.1

# ৪. Route delete
sudo ip route del 10.0.0.0/8
```

### **৫.৩ DNS Configuration**
```bash
# ১. Current DNS দেখো
cat /etc/resolv.conf

# ২. Temporary DNS set
sudo nano /etc/resolv.conf
# nameserver 8.8.8.8 যোগ করো

# ৩. Permanent DNS set (systemd-resolved)
sudo nano /etc/systemd/resolved.conf
# DNS=8.8.8.8 আনকমেন্ট করো
sudo systemctl restart systemd-resolved
```

---

## **৬. Network Troubleshooting Commands**

### **৬.১ Connectivity Issues**
```bash
# ১. Step-by-step connectivity check
ping 127.0.0.1        # Loopback চেক
ping 192.168.1.1      # রাউটার চেক
ping 8.8.8.8          # ইন্টারনেট চেক
ping google.com       # DNS চেক

# ২. MTU সমস্যা চেক
ping -M do -s 1472 8.8.8.8
# -M do = Don't Fragment
# -s 1472 = 1500 (MTU) - 28 (header)

# ৩. Packet loss চেক
ping -c 100 google.com
# শেষে statistics দেখাবে packet loss
```

### **৬.২ Bandwidth এবং Speed Test**
```bash
# ১. Speedtest-cli ইনস্টল
sudo apt install speedtest-cli

# ২. Speed test
speedtest-cli

# ৩. iftop দিয়ে real-time traffic
sudo apt install iftop
sudo iftop -i eth0
# -i = interface

# ৪. iperf3 দিয়ে bandwidth test
# সার্ভারে:
iperf3 -s

# ক্লায়েন্টে:
iperf3 -c server_ip

# ৫. nethogs (per-process bandwidth)
sudo apt install nethogs
sudo nethogs eth0
```

### **৬.৩ SSL/TLS Certificate Check**
```bash
# ১. SSL certificate দেখো
openssl s_client -connect google.com:443 -showcerts

# ২. Certificate expiration
echo | openssl s_client -connect google.com:443 2>/dev/null | openssl x509 -noout -dates

# ৩. Supported ciphers
nmap --script ssl-enum-ciphers -p 443 google.com
```

---

## **৭. Firewall এবং Security Commands**

### **৭.১ UFW (Uncomplicated Firewall)**
```bash
# ১. UFW status
sudo ufw status verbose

# ২. UFW enable
sudo ufw enable

# ৩. Port allow
sudo ufw allow 80/tcp
sudo ufw allow 22

# ৪. Port deny
sudo ufw deny 23

# ৫. Specific IP allow
sudo ufw allow from 192.168.1.100

# ৬. Delete rule
sudo ufw status numbered
sudo ufw delete 2  # rule number 2 delete
```

### **৭.২ iptables (Advanced Firewall)**
```bash
# ১. Current rules দেখো
sudo iptables -L -n -v
# -L = list
# -n = numeric
# -v = verbose

# ২. Rule add (allow SSH)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# ৩. Rule add (allow from specific IP)
sudo iptables -A INPUT -s 192.168.1.100 -j ACCEPT

# ৪. Rule add (block IP)
sudo iptables -A INPUT -s 10.0.0.1 -j DROP

# ৫. Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

---

## **৮. Network Monitoring Commands**

### **৮.১ Real-time Monitoring**
```bash
# ১. htop (process monitor)
sudo apt install htop
htop

# ২. nload (network load)
sudo apt install nload
nload eth0

# ৩. bmon (bandwidth monitor)
sudo apt install bmon
bmon

# ৪. vnstat (statistics)
sudo apt install vnstat
vnstat -d  # daily stats
vnstat -m  # monthly stats
```

### **৮.২ Log Analysis**
```bash
# ১. System logs
sudo journalctl -f  # follow mode
sudo journalctl --since "1 hour ago"

# ২. Auth logs
sudo tail -f /var/log/auth.log

# ৩. Kernel logs
sudo dmesg | grep -i network
```

---

## **৯. VPN এবং Tunneling Commands**

### **৯.১ SSH Tunneling**
```bash
# ১. Local port forwarding
ssh -L 3306:localhost:3306 user@remote_server
# localhost:3306 -> remote_server:3306

# ২. Remote port forwarding
ssh -R 8080:localhost:80 user@remote_server
# remote_server:8080 -> localhost:80

# ৩. Dynamic port forwarding (SOCKS proxy)
ssh -D 1080 user@remote_server
# SOCKS proxy port 1080
```

### **৯.২ OpenVPN**
```bash
# ১. OpenVPN ইনস্টল
sudo apt install openvpn

# ২. VPN কানেক্ট
sudo openvpn --config client.ovpn

# ৩. Disconnect
sudo killall openvpn
```

---

## **১০. Advanced Network Commands**

### **১০.১ tcpdump (Packet Capture)**
```bash
# ১. tcpdump ইনস্টল
sudo apt install tcpdump

# ২. সব প্যাকেট capture
sudo tcpdump -i eth0

# ৩. শুধু HTTP traffic
sudo tcpdump -i eth0 port 80

# ৪. Specific IP
sudo tcpdump -i eth0 host 192.168.1.100

# ৫. File এ save
sudo tcpdump -i eth0 -w capture.pcap

# ৬. Read from file
tcpdump -r capture.pcap
```

### **১০.২ mtr (My Traceroute)**
```bash
# ১. mtr ইনস্টল
sudo apt install mtr

# ২. Basic mtr
mtr google.com

# ৩. Report mode
mtr --report google.com

# ৪. নির্দিষ্ট প্যাকেট সাইজ
mtr -s 1000 google.com
```

### **১০.৩ arp (Address Resolution Protocol)**
```bash
# ১. ARP table দেখো
arp -a

# ২. Specific interface
arp -i eth0

# ৩. ARP entry add
sudo arp -s 192.168.1.100 aa:bb:cc:dd:ee:ff

# ৪. ARP entry delete
sudo arp -d 192.168.1.100
```

---

## **🎯 Quick Reference Cheat Sheet**

### **Daily Use Commands:**
```bash
# ১. IP দেখো
ip a

# ২. পিং করো
ping -c 4 google.com

# ৩. DNS চেক
dig google.com

# ৪. পোর্ট চেক
sudo ss -tulpn

# ৫. কানেক্টিভিটি চেক
curl ifconfig.me
```

### **Troubleshooting Sequence:**
```bash
# ধাপ ১: নিজের IP চেক
ip a

# ধাপ ২: রাউটারে পিং
ping 192.168.1.1

# ধাপ ৩: ইন্টারনেটে পিং
ping 8.8.8.8

# ধাপ ৪: DNS চেক
dig google.com

# ধাপ ৫: পোর্ট চেক
nc -zv google.com 80
```

---

## **📝 Practice Exercises**

### **Exercise 1: নিজের নেটওয়ার্ক ম্যাপ তৈরি**
```bash
# ১. নিজের subnet scan
nmap -sn 192.168.1.0/24

# ২. প্রতিটি ডিভাইসের IP লিখে রাখো
arp -a > network_devices.txt

# ৩. রাউটার পর্যন্ত পথ দেখো
traceroute google.com
```

### **Exercise 2: সার্ভার মনিটরিং স্ক্রিপ্ট**
```bash
#!/bin/bash
# monitoring.sh

echo "=== Network Status ==="
echo "IP Address: $(hostname -I)"
echo "Public IP: $(curl -s ifconfig.me)"
echo "DNS: $(dig +short google.com)"
echo "Ping to Google: $(ping -c 1 google.com | grep 'time=' | cut -d'=' -f4)"

# save to log
echo "$(date): Network check completed" >> /var/log/network_monitor.log
```

**রান করার জন্য:**
```bash
chmod +x monitoring.sh
./monitoring.sh
```

---

## **🚀 Pro Tips for Backend Developers**

### **১. API Response Time Monitor:**
```bash
#!/bin/bash
# api_monitor.sh

while true; do
    response=$(curl -w "%{time_total}\n" -o /dev/null -s http://localhost:8000/api/health)
    echo "$(date): Response time: ${response}s" >> api_response.log
    if (( $(echo "$response > 2.0" | bc -l) )); then
        echo "WARNING: Slow response detected!" | mail -s "API Alert" admin@example.com
    fi
    sleep 30
done
```

### **২. Database Connection Pool Monitor:**
```bash
# PostgreSQL connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# MySQL connections
mysql -u root -p -e "SHOW PROCESSLIST;"
```

### **৩. Load Balancer Health Check:**
```bash
#!/bin/bash
# health_check.sh

servers=("192.168.1.10:8000" "192.168.1.11:8000" "192.168.1.12:8000")

for server in "${servers[@]}"; do
    if curl -s --max-time 5 "http://$server/health" | grep -q "healthy"; then
        echo "$server: OK"
    else
        echo "$server: FAILED"
        # Auto-restart or alert
    fi
done
```

---

## **❓ যখন সমস্যা হবে**

### **১. "Network is unreachable"**
```bash
# সমাধান:
ip route show
# default gateway আছে কিনা চেক

# Gateway add:
sudo ip route add default via 192.168.1.1
```

### **২. "Name or service not known"**
```bash
# সমাধান:
cat /etc/resolv.conf
# DNS server ঠিক আছে কিনা

# Temporary fix:
sudo nano /etc/resolv.conf
# nameserver 8.8.8.8 লিখো
```

### **৩. "Connection refused"**
```bash
# সমাধান:
sudo ss -tulpn | grep :80
# পোর্টে কেউ লিসেন করছে কিনা
```

---

## **📚 Learning Path:**

**সপ্তাহ ১:** `ip`, `ping`, `dig`  
**সপ্তাহ ২:** `netstat/ss`, `nc`, `curl`  
**সপ্তাহ ৩:** `tcpdump`, `nmap`, `traceroute`  
**সপ্তাহ ৪:** `iptables`, `ufw`, Scripting

**প্রতিদিন ৫টি কমান্ড প্রাকটিস করো!**

---

**তোমার কোন প্রশ্ন থাকলে জিজ্ঞেস করো। প্রতিটি কমান্ডের ব্যাখ্যা জানতে চাইলে বলো!** 🚀

**এখন আমরা ৬নং টপিক থেকে শুরু করবো: "What is a Port and why ports are needed"**