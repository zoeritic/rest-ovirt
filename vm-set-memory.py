#!/usr/bin/python2
import os
import sys
import re
import getopt
from rest_helper.rest_helper import *






ip=Mhm2Mip(sys.argv[1])
Mipp=gen_ip(ip)
print_ok(Mipp)

glob=sys.argv[2]
vms_xml=get_vms_by_name_xml(Mipp,glob)
vm2id_d=get_all_id(vms_xml)

keys=vm2id_d.keys()
keys.sort()

for vmn in keys:

    print_info("Set Memory to  for VM:"+vmn)
    vm_set_memory(Mipp,vm2id_d[vmn])


