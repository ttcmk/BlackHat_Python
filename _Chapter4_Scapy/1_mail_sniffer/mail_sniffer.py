# -*- coding: utf-8 -*-

from scapy.all import *

# 数据包回调函数
def packet_callback(packet):
    return packet.show()

# 开启嗅探器
# sniff(filter="", iface="any", prn=function, count=N)
# filter参数设置一个BPF（wireshark）类型的过滤器，置空则嗅探所有数据包
# iface参数设置所有嗅探的网卡，留空则对所有网卡进行嗅探
# prn参数指定嗅探到指定条件的数据包时所调用的回调函数，这个回调函数以接收到的数据包对象作为唯一参数
# count参数设置嗅探的数据包个数，为空则无限
# 安装遇到错误：http://blog.csdn.net/marywang56/article/details/75314967
sniff(prn=packet_callback, count=1)