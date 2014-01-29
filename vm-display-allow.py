#!/usr/bin/python2

import os
import sys
import getopt
from rest_helper.rest_helper import *




class conf():
    ALLOW=True
    M_PLAT=''
    SET_ALL=False


def usage():
    print_info("Usage")
    message='''
Usage: %s [OPTION] 
    -m | --m-plat       \t: RhevM.
    -n | --not          \t: Enable strict user checking(Default is Disable check ,aka,)
    -a | --all          \t: set for all VMs in the RhevM.
    -E | --ere pattern  \t: select VMs by ere-pattern.
    -g | --glob pattern \t: select VMs by glob-pattern.
    -h | --help         \t: print this message.
'''%sys.argv[0]    
    print message

def main():
    
    try:
        opts,args=getopt.getopt(sys.argv[1:],'anm:E:g:h',['all','not','m-plat=','ere=','glob=','help'])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(-1)
    #yrt



    ere_pattern=''
    glob_pattern=''
    need_help=False

    vmlist=args[:]

    for o,a in opts:
        if o in ('-n','--no'):
            conf.ALLOW=False
        elif o in ('-m','--m-plat'):
            conf.M_PLAT=a
        elif o in ('-E','--ere'):
            ere_pattern=a
        elif o in ('-g','--glob'):
            glob_pattern=a
        elif o in ('-a','--all'):
            conf.SET_ALL=True
        elif o in ('-h','--help'):
            need_help=True
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(1)



#    allow_override(Mipp,vmid,disable=True,monitors=1,dtype='spice')

    ip=Mhm2Mip(conf.M_PLAT)
    print_ok(ip)
    Mipp=gen_ip(ip)

    vm2id_d={}

    if conf.SET_ALL:
        vms_xml=list_all_vms_xml(Mipp)
        vm2id_d=get_all_id(vms_xml)
    else:
        if ere_pattern!='':
#TODO
            vms_xml=list_all_vms_xml(Mipp)
            vm2id_d=get_all_id(vms_xml)
            for vmn in vm2id_d.keys():
                if not re.match(ere_pattern,vmn):
                    vm2id_d.pop(vmn)

        elif glob_pattern!='':
            print_err(glob_pattern)
            vms_xml=get_vms_by_name_xml(Mipp,glob_pattern)
            vm2id_d=get_all_id(vms_xml)
    #fi
#    vm2id_d=get_all_id(vms_xml)
    if len(vm2id_d)==0:
        usage()
        sys.exit(-3)

    keys=vm2id_d.keys()
    keys.sort()

    for vmn in keys:
        print_info('SET DISPLAY ALLOW '+str(conf.ALLOW)+' for VM:'+vmn)
        if conf.ALLOW==True:
            dis='true'
        else:
            dis='false'
        #fi
        vmid=vm2id_d[vmn]
        allow_override(Mipp,vmid,disable=dis,monitors=1,dtype='spice')
        #set_usb(Mipp,vm2id_d[vmn],type=conf.TYPE)

    if need_help:
        usage()



if __name__ == "__main__":
    main()





