#!/usr/bin/python2

import os
import sys
import getopt
import ConfigParser
from rest_helper.rest_helper import *






class conf():
    M_PLAT=''
    SET_ALL=False
    NIC='nic1'
    NETWORK=''
    TYPE='rtl8139'
    CONFIG_FILE='conf_nic_vm.ini'


def gen_conf_file(filename):

    config=ConfigParser.RawConfigParser()
    config.add_section('CONFIG')
    config.set('CONFIG','M_PLAT',conf.M_PLAT)
    config.set('CONFIG','SET_ALL',conf.SET_ALL)
    config.set('CONFIG','NIC',conf.NIC)
    config.set('CONFIG','NETWORK',conf.NETWORK)
    config.set('CONFIG','TYPE',conf.TYPE)

    with open(filename,'wb') as configfile:
        config.write(configfile)

    print_info( "----------------------------------")
    print_info( "[CONFIG]")
    print_info( "M_PLAT    =\t"+conf.M_PLAT)
    print_info( "SET_ALL   =\t"+str(conf.SET_ALL))
    print_info( "NIC       =\t"+str(conf.NIC))
    print_info( "NETWORK   =\t"+str(conf.NETWORK))
    print_info( "TYPE      =\t"+conf.TYPE)
    print_info( "----------------------------------")



def read_conf_file(filename,conf):
    config=ConfigParser.RawConfigParser()

    config.read(filename)
    configc=config


    conf.M_PLAT=configc.get('CONFIG','M_PLAT')
    conf.SET_ALL=configc.getboolean('CONFIG','SET_ALL')
    conf.NIC=configc.get('CONFIG','NIC')
    conf.NETWORK=configc.get('CONFIG','NETWORK')
    conf.TYPE=configc.get('CONFIG','TYPE')

    print_info( "----------------------------------")
    print_info( "[CONFIG]")
    print_info( "M_PLAT    =\t"+conf.M_PLAT)
    print_info( "SET_ALL   =\t"+str(conf.SET_ALL))
    print_info( "NIC       =\t"+str(conf.NIC))
    print_info( "NETWORK   =\t"+str(conf.NETWORK))
    print_info( "TYPE      =\t"+conf.TYPE)
    print_info( "----------------------------------")




def usage():
    message='''
Usage: %s [OPTIONS..]
        -i|--ini conf_nic.ini   \t: from which file to get configuration,if not specified,the `conf_nic.ini' will be read,or if not exist the file within the directory, the program will generate one.
        -m|--m-plat Mhostname   \t: the Hostname of Rhev-M ,such as `s-m14'.
        -n|--net net-name       \t: the name of network you want to set to nic.
        -N|--nic nic-name       \t: the nic name of VMs.
        -t|--type nic-type      \t: the nic type(default type `rtl8139').
        -E|--ere re-pattern     \t: the nic of which the VMs's name matched by the RE will be set.
        -g|--glob glob-pattern  \t: the name of VMs matched by the glob will be set.
        -a|--all                \t: set nic for all VMs within the Rhev-M.
        -R|--rtl8139            \t: the same of `-t rtl8139'.
        -V|--virtio             \t: the same of `-t virto'.
        
        -h|--help               \t: print this message.

'''%sys.argv[0]
    print_info( message)


def main():


    try:
        opts,args=getopt.getopt(sys.argv[1:],':m:n:N:t:E:g:aRVh',['ini=','m-plat=','net=','nic=','type=','ere=','glob=','all','rtl8139','virtio','help'])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(1)
    #yrt
    print_info(args)
    need_help=False
    have_conf_file=False
    if not os.path.exists(conf.CONFIG_FILE):
        gen_conf_file(conf.CONFIG_FILE)
        print_info('Config-file: '+conf.CONFIG_FILE+' generation!!')
    else:
        read_conf_file(conf.CONFIG_FILE,conf)
    #fi

    ere_pattern=''
    glob_pattern=''
    vmlist=args[:]


    for o,a in opts:
        if o in ('-i','--ini'):
            have_conf_file=True
            conf.CONFIG_FILE=a
            read_conf_file(conf.CONFIG_FILE,conf)
        elif o in ('-m','--m-plat'):
            conf.M_PLAT=a
        elif o in ('-n','--net'):
            conf.NETWORK=a
        elif o in ('-N','--nic'):
            conf.NIC=a
        elif o in ('-t','--type'):
            conf.TYPE=a
        elif o in ('-E','--ere'):
            conf.SET_ALL=False
            ere_pattern=a
        elif o in ('-g','--glob'):
            conf.SET_ALL=False
            glob_pattern=a
        elif o in ('-a','--all'):
            conf.SET_ALL=True
        elif o in ('-R','--rtl8139'):
            conf.TYPE='rtl8139'
        elif o in ('-V','--virtio'):
            conf.TYPE='virtio'
        elif o in ('-h','--help'):
            need_help=True
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(2)
        #fi

    #rof

    print_ok("conf.M_PLAT  : "+str(conf.M_PLAT))
    print_ok("conf.SET_ALL : " +str(conf.SET_ALL))
    print_ok("conf.NIC     : " +str(conf.NIC))
    print_ok("conf.NETWORK : " +str(conf.NETWORK))
    print_ok("conf.TYPE    : " +str(conf.TYPE))



    Mip=Mhm2Mip(conf.M_PLAT)
    Mipp=gen_ip(Mip)
    print_ok(Mip)

    vm2id_d={}

    if conf.SET_ALL:
        vms_xml=list_all_vms_xml(Mipp)
        vm2id_d=get_all_id(vms_xml)
    else:
        if ere_pattern!='':
            vms_xml=list_all_vms_xml(Mipp)
            vm2id_d=get_all_id(vms_xml)
            for vmn in vm2id_d.keys():
                if not re.match(ere_pattern,vmn):
                    vm2id_d.pop(vmn)
                #fi
            #rof
        elif glob_pattern!='':
            #print_err(glob_pattern)
            vms_xml=get_vms_by_name_xml(Mipp,glob_pattern)
            vm2id_d=get_all_id(vms_xml)
    #fi
    
    keys=vm2id_d.keys()
    keys.sort()

    for vmn in keys:
        vmid=vm2id_d[vmn]
        nic2id_d=get_vm_nics(Mipp,vmid)
        nics_num=len(nic2id_d)
        if nics_num==0:
            print_info('No Nics attached to VM: '+vmn)
        elif nics_num!=1:
            print_info('There '+str(nics_num)+' Nics attached to VM: '+vmn)
        #fi
        if conf.NIC in nic2id_d.keys():
            nicid=nic2id_d[conf.NIC]
            vm_modify_nic(Mipp,vmid,nicid,vlan_name=conf.NETWORK,nic_name=conf.NIC,nic_type=conf.TYPE)
        else:
            vm_add_nic(Mipp,vmid,vlan_name=conf.NETWORK,nic_name=conf.NIC,nic_type=conf.TYPE)
        #fi


    if need_help:
        usage()


if __name__ == '__main__':
    main() 

