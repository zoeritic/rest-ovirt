#!/usr/bin/python2


import os
import sys
import getopt
from rest_helper.rest_helper import *

class conf():
    HOST=''
    M_PLAT=''
#    VMSELECT=[]
#    STATE=''



def usage():
    message='''

Usage: %s [OPTIONS.] VM0* VM1*
        -m|--m-plat       \t: the Rhev-M hostname,such as `s-m14'.
        -k|--kill         \t: kill the suspicious VMs.
        -g|--glob pattern \t: select vms by glob.
        -E|--ere pattern  \t: select vms by ERE.
        -h|--help         \t: print this message.

CAUTION: This Program MUST be run on Rhev-H ,in which vdsm running.

'''%sys.argv[0]
    print_info(message)



def check_nr(sd):
    if (sd['cpu.current.hypervisor']=='110' or sd['cpu.current.hypervisor']=='100') and (sd['cpu.current.total']=='110' or sd['cpu.current.total']=='100'):# or sd['cpu.current.total']=='100':
        return True

def print_statistics_of_vm(sd):
    '''
{'cpu.current.guest': '0', 'memory.used': '0', 'cpu.current.hypervisor': '0', 'memory.installed': '1073741824', 'cpu.current.total': '0'}
'''
    if check_nr(sd):
        print '---->>',
    for it in sd.keys():
        if not it.startswith('memory'):
            print it+' : '+sd[it]+'\t',
    print


def main():
    try:
        opts,args=getopt.getopt(sys.argv[1:],'m:khg:',['m-plat=','kill','help','glob='])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(1)
    #yrt


    ere_pattern=''
    glob_pattern=''

    for o,a in opts:
        if o in ('-m','--m-plat'):
            conf.M_PLAT=a
        elif o in ('-g','--glob'):
            glob_pattern=a
        elif o in ('-E','--ere'):
            ere_pattern=a
        elif o in ('-h','--help'):
            need_help=True
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(3)
        #fi
    #rof


    mip=Mhm2Mip(conf.M_PLAT)
    Mipp=gen_ip(mip)
    print_ok("Mipp: "+Mipp)

    vm2id_d={}

    if glob_pattern!='':
        vmxml=get_vms_by_name_xml(Mipp,glob_pattern)
        vm2id_d=get_all_id(vmxml)
#    print_err("=================")
    elif ere_pattern!='':
        vms_xml=list_all_vms_xml(Mipp)
        vm2id_d=get_all_id(vms_xml)
        for vmn in vm2id_d.keys():
            if not re.match(ere_pattern,vmn):
                vm2id_d.pop(vmn)
            #fi
        #rof
    #fi




    keys=vm2id_d.keys()
    keys.sort()
    for vm in keys:
        vmid=vm2id_d[vm]
        statistic_xml=get_vm_link_of(Mipp,vmid)
        s_d=statistics_of_vm(statistic_xml)
        print vm+':: ',
        print_statistics_of_vm(s_d)








if __name__ =='__main__':
    main()
