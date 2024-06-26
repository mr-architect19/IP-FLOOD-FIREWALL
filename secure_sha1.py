#!/usr/bin/python
from netaddr import IPNetwork
import os,time,argparse,socket,pprint
from scapy.all import *
import sys
from datetime import datetime, time

def querysniff(pkt):
        if IP in pkt:
                ip_src=pkt[IP].src
                ip_dst=pkt[IP].dst
                if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
                        print ("Source : "+str(ip_src) +" Destination: "+str(ip_dst) +"DNS Query for Domain "+pkt.getlayer(DNS).qd.qname)


def queryguard(pkt): 
        if IP in pkt:
                ip_src=pkt[IP].src
                ip_dst=pkt[IP].dst
                if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
                        domain=pkt.getlayer(DNS).qd.qname
                        bannedlist=open("dnslist","r").read()
                        bannedlist=bannedlist.split()
                        for url in bannedlist:
                         os.popen("iptables -I FORWARD -p udp --dport 53 -m string --string '"+url+"' -j DROP")
                         if (url in domain):
                                print (ip_src+" is looking for a blocked domain ",domain)
                                iplist=os.popen("host "+domain+" | grep 'has addr' | awk '{ print $4;}'").read().split()
                                for ip in iplist:
                                                os.popen("iptables -I FORWARD -d "+ip+" -j DROP")
                                                print ("Domain resolved and Blocked!!!")
                                                print ("IP Blocked: ",ip)


def ipsniff(pkt): 
        if IP in pkt:
                ip_src=pkt[IP].src
                ip_dst=pkt[IP].dst
                ip_src_port=pkt[IP].sport
                ip_dst_port=pkt[IP].dport
                print ("Source : "+str(ip_src) +":"+str(ip_src_port)+" Destination: "+str(ip_dst)+":"+str(ip_dst_port))

def arpsniff(pkt): 
    if ARP in pkt and pkt[ARP].op in (1,2):
        return pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")




parser = argparse.ArgumentParser()

parser.add_argument('-delay', action='store', default="none",
                    dest='delay',
                    help='Adds a delay between packets to slow the network')



parser.add_argument('-dnsguard', action='store', default="none",
                    dest='dnsguard',
                    help='Enable DNS Guard and automatically ban DNS Resolved IP Addresses of unwated URLs in given list')

parser.add_argument('-arpguard', action='store_true', default=False,
                    dest='arpguard',
                    help='Enable ARP Guard and automatically ban ARP Spoofing hosts')

parser.add_argument('-showlogs', action='store', default="none",
                    dest='showlogs',
                    help='Show clean logs if present.. arguments: ALL,HTTP,DNS,TCP,UDP,IP')

parser.add_argument('-banCountry', action='store', default="none",
                    dest='bancountry',
                    help='Ban all IP addresses coming from given country italy--> it ..pakistan --> pk')

parser.add_argument('-proxy', action='store', default="none",
                    dest='loadproxy',
                    help='Route HTTP and HTTPS traffic to an Internal or External Transparent Proxy .. \n Example: -proxy 192.168.1.5:3128')

parser.add_argument('-trafficlimit', action='store', default="none",
                    dest='trafflimit',
                    help='Limit traffic rate... 10/s = 10 packet per second .. 10/m = 10 per minute ..10/h per hour')

parser.add_argument('-timerange', action='store', default="none",
                    dest='timerange',
                    help='Time range intervall that will be applied on rule or SDS argument \nExample: -timerange 09:00,18:00 ')

parser.add_argument('-log', action='store_true', default=False,
                    dest='log',
                    help='Enable packets logging on /var/log')

parser.add_argument('--blacklist', action='store', default="none",
                    dest='blacklist',
                    help='Load a list with banned keywords\IP\Domains that will be applied on the firewall')

parser.add_argument('--whitelist', action='store', default="none",
                    dest='whitelist',
                    help='Load a list with the only permitted keywords\IP\Domains on the firewall')

parser.add_argument('--loadpcap', action='store', default="none",
                    dest='loadpcap',
                    help='Load a list with banned keywords\IP\Domains that will be applied on the firewall')

parser.add_argument('--loadweb', action='store', default="none",
                    dest='loadweb',
                    help='Load a list with banned keywords\IP\Domains from the web')

parser.add_argument('--GUI', action='store_true', default=False,
                    dest='gui',
                    help='Load the webGUI and start browser to check stats\traffic analysis')

parser.add_argument('--nopolicy', action='store', default="none",
                    dest='nopolicy',
                    help='Set "DENY" default policy on given CHAIN.. example: FORWARD,INPUT,OUTPUT')

parser.add_argument('--yespolicy', action='store', default="none",
                    dest='yespolicy',
                    help='Set "ACCEPT" default policy on given CHAIN.. example: FORWARD,INPUT,OUTPUT')

parser.add_argument('--captiveportal', action='store', default="none",
                    dest='captive',
                    help='Enable the captive portal and any address is being redirected to the given address')

parser.add_argument('--dns-redirect', action='store', default="none",
                    dest='dnsre',
                    help='Redirect all DNS queries to given dns sever address')

parser.add_argument('--redirect-to', action='store', default="none",
                    dest='redto',
                    help='Redirect all traffic to given address')

parser.add_argument('--no-dns', action='store_true', default=False,
                    dest='nodns',
                    help='Removes DNS redirect')

parser.add_argument('--icmp-redirect', action='store', default="none",
                    dest='icmpre',
                    help='Redirect all ICMP Requests to given address')

parser.add_argument('--no-icmp', action='store_true', default=False,
                    dest='noicmp',
                    help='Removes ICMP redirect')


parser.add_argument('-R', action='store_true', default=False,
                    dest='flush',
                    help='Restore default iptables rules')

parser.add_argument('-S', action='store_true', default=False,
                    dest='save',
                    help='Save iptables rules on startup **warning** deletes old ones')

parser.add_argument('-killmitm', action='store_true', default=False,
                    dest='killmitm',
                    help='Kill any Offensive SDS Firewall doing mitm')


parser.add_argument('-rule', action='store', dest='rule', default=False, help='Manually create firewall rules via an easy syntax language')


parser.add_argument('--deny', action='store', dest='denyrules', default="none", help='Write deny rules')



parser.add_argument('--permit', action='store', dest='permitrules', default="none", help='Write permit rules')



parser.add_argument('--spoof', action='store', default="none", dest='spoof', help='Force Firewall to all hosts even if not connected to our machine directly..\n Specify Default gateway')


os.popen('echo "1" > /proc/sys/net/ipv4/ip_forward')


results = parser.parse_args()





if not(results.delay=="none"):  
        if(results.delay=="nope"):
                os.popen("tc qdisc del dev eth0 root")
        else:
                delay=results.delay+"ms"
                os.popen("tc qdisc add dev eth0 root netem delay "+delay)
                print ("Added a delay of "+delay)



if not(results.timerange=="none"): 
        interval=results.timerange
        interval=interval.split(",")
        print ("interval: "+interval)
        time1=interval[0]
        time2=interval[1]
        timeout="-m time --timestart "+time1+" --timestop "+time2
else:
        timeout=""



if not(results.bancountry=="none"): 
      code=results.bancountry
      iplist=os.popen("curl  http://www.ipdeny.com/ipblocks/data/countries/"+code+".zone").read()
      iplist=iplist.split()
      for ip in iplist:
        os.popen("iptables -I FORWARD -d "+ip+" -j DROP")
        os.popen("iptables -I INPUT -d "+ip+" -j DROP")
        os.popen("iptables -I OUTPUT -d "+ip+" -j DROP")
        print (ip+" DENIED")


if not(results.showlogs=="none"): 
      res=results.showlogs
      if("dns" in res): 
        
        print (os.popen("""tail -n 100 /var/log/syslog | grep DNS | awk '{$5="  ";  $9="   ";  $10=""; $14="   "; $15=""; $17="  "; $18=""; $23="";  print $i }'""").read())

      if("www" in res):
        print (os.popen("""tail -n 100 /var/log/syslog | grep WWW | awk '{$5="  ";  $9="   ";  $10=""; $14="   "; $15=""; $17="  "; $18=""; $23="";  print $i }'""").read())

      if("credentials" in res):
         print (os.popen("""tail -n 100 /var/log/syslog | grep -e USER -e PASSW | awk '{$5="  ";  $9="   ";  $10=""; $14="   "; $15=""; $17="  "; $18=""; $23="";  print $i }'""").read())



if not(results.dnsguard=="none"): 
        urlfilter=results.dnsguard
        stdout = sys.stdout
        capturer = StringIO.StringIO()
        sys.stdout=capturer
        sniff(iface="eth0",filter="port 53",prn=queryguard, store= 0,count=100)
        sys.stdout = stdout
        raw_dnslog= capturer.getvalue()
        print (raw_dnslog)
        print ("\n\n")




if(results.arpguard): 
        stdout = sys.stdout
        capturer = StringIO.StringIO()
        beginscan= datetime.now()
        sys.stdout = capturer
      
        sniff(prn=arpsniff, filter="arp", store=0,count=10)
        sys.stdout = stdout
        
        raw_arplist= capturer.getvalue()
        finishscan = datetime.now()
        print ("Started at: ",beginscan)
        print ("Finished at: ",finishscan)
        file=open("arplist","w").write(raw_arplist)
        times=os.popen("sort arplist | uniq --count | sort -nr").read().split()[0]
        seconds=str((finishscan - beginscan).seconds)
        print ("Found MAC Flooded for "+times+" times in "+seconds+" seconds")
        spoofedmac=os.popen("sort arplist | uniq --count | sort -nr | awk '{ print $2; }' | grep 1").read().split()
        spoofedmac=str(spoofedmac[0])
        if not(seconds>10 or times<5):
                print ("Attacker is: "),spoofedmac
                os.popen("iptables -A INPUT -m mac --mac-source "+spoofedmac+" -j DROP")
                os.popen("iptables -A FORWARD -m mac --mac-source "+spoofedmac+" -j DROP")
                print ("Banned "+spoofedmac+" from the network... ARP Spoof DETECTED!\n")
                os.popen("rm arplist")
        else:
                print ("None is doing MAC Flooding")
                print ("Most duplicate MAC is: "),spoofedmac


if not (results.trafflimit=="none"):
      tl=results.trafflimit
      ## TODO 
      os.popen("iptables -I INPUT -p tcp -m limit --limit "+tl+" "+timeout+" -j ACCEPT")
      os.popen("iptables -I OUTPUT -p tcp -m limit --limit "+tl+" "+timeout+" -j ACCEPT")
      os.popen("iptables -I FORWARD -p tcp -m limit --limit "+tl+" "+timeout+" -j ACCEPT")
      os.popen("iptables -I INPUT -p udp -m limit --limit "+tl+" "+timeout+" -j ACCEPT")
      os.popen("iptables -I OUTPUT -p udp -m limit --limit "+tl+" "+timeout+" -j ACCEPT")
      os.popen("iptables -I FORWARD -p udp -m limit --limit "+tl+" "+timeout+" -j ACCEPT")


if not(results.loadpcap == "none"):
                        print ("Reading capture file and parsing ip addresses")
                        print ("Only ip addresses found on .pcap will be allowed to pass on this firewall")
                        try:
                                allowedIP=os.popen("""tshark  -o column.format:'"Source", "%s"' -r """+results.loadpcap+" |sort|uniq").read()
                                print (allowedIP)
                                for line in allowedIP.split():
                                        try:
                                                 socket.inet_aton(line)
                                                 print ("Loaded from pcap  ",line)
                                                 os.popen("iptables -I FORWARD -p ALL -m string --string  "+line+" --algo kmp "+timeout+" -j ACCEPT")
                                        except:
                                                print ("This isn't an IP")
                                os.popen("iptables -P FORWARD DROP")
                        except:
                                print ("Error Parsing capture")
if not(results.blacklist =="none"):
                            blacklist=results.blacklist
                            try:
                                f=open(blacklist,"r") 
                                filterlist=f.read()  
                                for line in filterlist.split(): 
                                        if(";" in line): 
                                                print ("Ignore comment")
                                        else: 
                                                try:
                                                        socket.inet_aton(line)
                                                        print ("I'm an ipv4! ",line)
                                                      
                                                        os.popen("iptables -I FORWARD -p ALL -m string --string  "+line+" --algo kmp  -j DROP")
                                                        os.popen("iptables -I FORWARD -p ALL -m string --string  "+line+" --algo kmp  -j LOG --log-prefix 'BLACKLIST-SDS'")
                                                except: 
                                                        os.popen("iptables -I FORWARD -p tcp --match multiport --dports 80,443 -m string --string "+line+" --algo kmp -j DROP")
                                                        os.popen("iptables -I FORWARD -p udp --dport 53 -m string --string "+line+" --algo kmp -j DROP")
                                                        os.popen("iptables -I FORWARD -p ALL -m string --string  "+line+" --algo kmp -j LOG --log-prefix 'BLACKLIST-SDS'")
                                                        print ("added blacklist rule: ",line)
                            except:
                                print ("Can't load filter list")
if not(results.whitelist =="none"):
                            whitelist=results.whitelist
                            try:
                                f=open(whitelist,"r") 
                                filterlist=f.read()
                                for line in filterlist.split():
                                        if(";" in line):
                                                print ("Ignore comment")
                                        else:
                                                try:
                                                        socket.inet_aton(line)
                                                        print ("I'm an ipv4! ",line)
                                                
                                                        os.popen("iptables -I FORWARD -p ALL -m string --string  "+line+" --algo kmp "+timeout+" -j ACCEPT")
                                                        os.popen("iptables -I FORWARD -p ALL -m string --string  "+line+" --algo kmp -j LOG --log-prefix 'WHITELIST-SDS'")
                                                except: 
                                                        os.popen("iptables -I FORWARD -p tcp --match multiport --dports 80,443 -m string --string "+line+" --algo kmp "+timeout+" -j ACCEPT")
                                                        os.popen("iptables -I FORWARD -p udp --dport 53 -m string --string "+line+" --algo kmp "+timeout+" -j ACCEPT")
                                                        os.popen("iptables -I FORWARD -p ALL -m string --string  "+line+" --algo kmp -j LOG --log-prefix 'WHITELIST-SDS'")
                                                        print ("added whitelist rule: ",line)
                            except:
                                print ("Can't load filter list")


if not(results.nopolicy == "none"):
    chain=results.nopolicy
    os.popen("iptables -P "+chain+" DENY")


if not(results.yespolicy == "none"):
    chain=results.yespolicy
    os.popen("iptables -P "+chain+" ACCEPT")



if(results.log):
    os.popen("iptables -I FORWARD -p all -j LOG --log-prefix 'GENERAL-LOG'")
       

    os.popen("iptables -I FORWARD -p all -m string --string 'jpg' --algo kmp  -j LOG --log-prefix 'JPG-SDS'")
    os.popen("iptables -I FORWARD -p all -m string --string 'gif' --algo kmp  -j LOG --log-prefix 'GIF-SDS'")
    os.popen("iptables -I FORWARD -p all -m string --string 'png' --algo kmp  -j LOG --log-prefix 'PNG-SDS'")
    os.popen("iptables -I FORWARD -p all -m string --string 'mp4' --algo kmp  -j LOG --log-prefix 'MP4-SDS'")

    os.popen("iptables -I FORWARD -p tcp -m multiport --dports 80,443 -j LOG --log-prefix 'WWW-SDS' ")

    os.popen("iptables -I FORWARD -p udp --dport 53 -j LOG --log-prefix 'DNS-SDS'")
    
    os.popen("iptables -I FORWARD -p all -m string --string 'passw' --algo kmp -j LOG --log-prefix 'PASSWORD-SDS'")
    os.popen("iptables -I FORWARD -p all -m string --string 'user' --algo kmp  -j LOG --log-prefix 'USERNAME-SDS'")


if(results.flush):
        os.popen("iptables-restore < /etc/iptables/rules.v4")


if not(results.captive== "none"):
        cpIP=results.captive
        os.popen("iptables -P FORWARD DENY")
        os.popen("iptables -P PREROUTING DENY")
        os.popen("iptables -P POSTROUTING DENY")
        os.popen("iptables -t nat -I PREROUTING -p tcp --dport 443 "+timeout+" -j DNAT --to-destination "+cpIP+":80")
        os.popen("iptables -t nat -I PREROUTING -p tcp --dport 80 "+timeout+" -j DNAT --to-destination "+cpIP+":80")

if not(results.dnsre =="none"):
       dnsServer=results.dnsre
       os.popen("iptables -t nat -I PREROUTING -p udp --dport 53 "+timeout+" -j DNAT --to-destination "+dnsServer+":53")

if not(results.redto =="none"):
       ip=results.redto
       os.popen("iptables -t nat -I PREROUTING -s 0/0 "+timeout+" -j DNAT --to-destination "+ip)


if(results.nodns):
        ip=os.popen("""iptables -t nat -L PREROUTING  | grep "domain to:" | awk '{ print $8; exit }'""").read().replace("to:","")
        cleanip=ip.strip()
        os.popen("iptables -t nat -D PREROUTING -p udp --dport 53 "+timeout+" -j DNAT --to-destination "+cleanip)


if not(results.icmpre == "none"):
      print ("Redirecting icmp!")
      fakedest=results.icmpre
      os.popen("iptables -t nat -I PREROUTING -p icmp --icmp-type echo-request "+timeout+" -j DNAT --to-destination "+fakedest)

if(results.noicmp):
        ip=os.popen("""iptables -t nat -L PREROUTING  | grep "icmp echo-request to:" | awk '{ print $8; exit }'""").read().replace("to:","")
        cleanip=ip.strip()
        os.popen("iptables -t nat -D PREROUTING -p icmp --icmp-type echo-request "+timeout+" -j DNAT --to-destination "+cleanip)

if(results.save):
        os.popen("iptables-save >> /etc/iptables/rules.v4")
        print ("Saved rules!")

if(results.rule):
  print ("Manual rules are being added!")
  permit=str(results.permitrules)
  deny=str(results.denyrules)
  if("icmp" in permit):
        os.popen("iptables -I FORWARD -p icmp --icmp-type 8 "+timeout+" -j ACCEPT")
  elif("icmp" in deny):
        os.popen("iptables -I FORWARD -p icmp --icmp-type 8 "+timeout+" -j DROP")

  print ("using rules ",deny)
  if("tcp" in deny):

      if("http" in deny):
         os.popen("iptables -I FORWARD -p tcp --dport 80 "+timeout+" -j DROP")
      if("https" in deny):
        os.popen("iptables -I FORWARD -p tcp --dport 443 "+timeout+" -j DROP")
      if("ftp" in deny):
        os.popen("iptables -I FORWARD -p tcp --dport 21 "+timeout+" -j DROP")
      if("dns" in deny):
         os.popen("iptables -I FORWARD -p tcp --dport 53 "+timeout+" -j DROP")
  else:

      if("http" in deny):
         os.popen("iptables -I FORWARD -p udp --dport 80 "+timeout+" -j DROP")
      if("https" in deny):
        os.popen("iptables -I FORWARD -p udp --dport 443 "+timeout+" -j DROP")
      if("ftp" in deny):
        os.popen("iptables -I FORWARD -p udp --dport 21 "+timeout+" -j DROP")
      if("dns" in deny):
         os.popen("iptables -I FORWARD -p udp --dport 53 "+timeout+" -j DROP")
  ### PERMIT RULES
  print ("using rules ",permit)
  if("tcp" in permit):

     if("http" in permit):
          os.popen("iptables -I FORWARD -p tcp --dport 80 "+timeout+" -j ACCEPT")
     if("https" in permit):
         os.popen("iptables -I FORWARD -p tcp --dport 443 "+timeout+" -j ACCEPT")
     if("ftp" in permit):
         os.popen("iptables -I FORWARD -p tcp --dport 21 "+timeout+" -j ACCEPT")
     if("icmp" in permit):
        os.popen("iptables -I FORWARD -p icmp --icmp-type 8 "+timeout+" -j ACCEPT")
     if("dns" in permit):
         os.popen("iptables -I FORWARD -p tcp --dport 53 "+timeout+" -j ACCEPT")

  else:

     if("http" in permit):
          os.popen("iptables -I FORWARD -p udp --dport 80 "+timeout+" -j ACCEPT")
     if("https" in permit):
         os.popen("iptables -I FORWARD -p udp --dport 443 "+timeout+" -j ACCEPT")
     if("ftp" in permit):
         os.popen("iptables -I FORWARD -p udp --dport 21 "+timeout+" -j ACCEPT")
     if("icmp" in permit):
        os.popen("iptables -I FORWARD -p icmp --icmp-type 8 "+timeout+" -j ACCEPT")
     if("dns" in permit):
         os.popen("iptables -I FORWARD -p udp --dport 53 "+timeout+" -j ACCEPT")


if not(results.spoof=="none"): 
        ipnet=results.spoof  
        iplist=os.popen("nmap -sP "+ipnet+" | grep 'Nmap scan' | awk '{ print $5; }'").read()
        iplist=iplist.split()
        dgip=os.popen("ip route show | grep 'default' | awk '{print $3}' ").read()
        dgip=dgip.split()[0]
        print ("Spoofing "+dgip+"\n\n")
        for ip in iplist:
                print (ip)
                os.popen("nohup arpspoof -t "+ip+" "+dgip+" >/dev/null 2>&1 &")

if not(results.loadproxy=="none"):
                proxy=results.loadproxy
                os.popen("iptables -t nat -A PREROUTING -m multiport -p tcp --dports 80,443 -j DNAT --to "+proxy)
                os.popen("iptables -t nat -I FORWARD -d "+proxy+" -j ACCEPT")



if(results.killmitm):
    os.popen("killall arpspoof")
    os.popen("killall tcpkill")
