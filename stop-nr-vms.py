#!/usr/bin/python2


import os
import sys
import getopt
import subprocess
from rest_helper.rest_helper import *

class conf():
    HOST=''
    KILL=False
#    VMSELECT=[]
#    STATE=''



def usage():
    message='''

Usage: %s [OPTIONS.] VM0* VM1*
        -m|--m-plat M    \t: the Rhev-M hostname,such as `s-m14'.
        -s|--s-m         \t: all students M.
        -t|--t-m         \t: all teachers M.
        -k|--kill        \t: kill the suspicious VMs.
        -h|--help        \t: print this message.

CAUTION: This Program MUST be run on Rhev-H ,in which vdsm running.

'''%sys.argv[0]
    print_info(message)



def check_nr(sd):
    if sd['cpu.current.hypervisor']=='110':# or sd['cpu.current.total']=='100':
        return True
    else:
        return False

def print_statistics_of_vm(sd):
    '''
{'cpu.current.guest': '0', 'memory.used': '0', 'cpu.current.hypervisor': '0', 'memory.installed': '1073741824', 'cp
'''
    if check_nr(sd):
        print '---->>',
    for it in sd.keys():
        if not it.startswith('memory'):
            print it+' : '+sd[it]+'\t',
    print





def kill_vm_by_name(hip,vmname):
    CMD=r"vdsClient -s 0 list table |grep "+vmname+r' |awk \"{print \\\$2}\" |xargs kill -9 '
    rt=do_SSH(hip,CMD)
    #print_info(rt)


def kill_nr_vms(hip,state=r"\"Up\\*\""):
    CMD=r"vdsClient -s 0 list table |grep "+state+r' |awk \"{print \\\$2}\" |xargs kill -9 '
    rt=do_SSH(hip,CMD)
    print_info(rt)






def list_hostsip_of_M(Mipp):
    xml=list_all_hosts_xml(Mipp)
    doc=etree.fromstring(xml)
    hostsl=doc.findall('host')
    hostip_d={}
    for host in hostsl:
        name=host.find('name').text
        addr=host.find('address').text
        hostip_d[name]=addr
    return hostip_d



def do_SSH(HIP,cmd='hostname',user='root',password='redhat'):
#    CMD='ssh '+user+'@'+HIP+' '+cmd

    print_ok("H: "+HIP)
    print_ok('Executing: '+cmd)
    EXPECT_SSH_CMD='''
    expect  -c '
    set ip %(IP)s
    set password %(PASSWD)s
    set timeout 5
    spawn ssh root@$ip
    expect {
    "*yes/no" {send "yes\\r";exp_continue}
    "*password:" {send "$password\\r"}
    }
    expect "*]#"
    send "%(CMD)s\\r"
    expect "*]#"
    send "exit\\r"
    '

    '''%{'IP':HIP,'PASSWD':password,'CMD':cmd}

    print EXPECT_SSH_CMD
#    sys.exit(0)

    p=subprocess.Popen(EXPECT_SSH_CMD,shell=True,stdout=subprocess.PIPE,close_fds=True)
    SSH_OUT=p.stdout.read().strip()
#    print '======================='
#    print_info(SSH_OUT)
#    print "-----------------------"
#    vdsinfo=re.search(r"vdsClient.*\ni\(.*\)[",SSH_OUT).group(0)
    return SSH_OUT












def main():
    try:
        opts,args=getopt.getopt(sys.argv[1:],'m:khast',['m-plat=','kill','help','all','tm','sm'])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(1)
    #yrt

    MNlist=args

#    conf.HOST=os.popen('hostname').read().strip()
#    print_info('!! HOST: '+conf.HOST)



    for o,a in opts:
        if o in ('-k','--kill'):
            conf.KILL=True
        elif o in ('-s','--sm'):
            MNlist=gc.MS_LIST
        elif o in ('-t','--tm'):
            MNlist=gc.MH_LIST
        elif o in ('-a','--all'):
            MNlist=gc.M_LIST
        elif o in ('-h','--help'):
            need_help=True
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(3)
        #fi
    #rof


 #   mip=Mhm2Mip(conf.M_PLAT)
 #   Mipp=gen_ip(mip)
#    tvm2id=get_vms_by_host(Mipp,conf.HOST)

#    keys=tvm2id.keys()
#    keys.sort()

#    for vm in keys:
#        vm2p=vdsClient_wrap(vm)
#        vmid=tvm2id[vm]
#        vmpid=vm2p[vm]
#        print_warn(" Suspicious VM: "+vm)
#        if tokill:
#            kill_vm(vm,vmpid)







    for mn in MNlist:
        mip=Mhm2Mip(mn)
        hnlst=Mhm2Hhm(mn)
        ip=Mhm2Mip(mn)
        Mipp=gen_ip(ip)
        vm2hip={}
        haddrd=list_hostsip_of_M(Mipp)

        rt_xml=list_all_vms_xml(Mipp)
        vm2hip=get_host_of_vms(rt_xml)
        vm2id=get_all_id(rt_xml)

        keys=vm2hip.keys()
        keys.sort()
        for vm in keys:
            hip=vm2hip[vm][1]
            vmid=vm2id[vm]
            sxml=get_vm_link_of(Mipp,vmid)
            sd=statistics_of_vm(sxml)
            if check_nr(sd):
                print_statistics_of_vm(sd)

                if conf.KILL==True:
                    kill_vm_by_name(hip,vm)
                    print_ok("VM: "+vm+" has been killed!!")
                else:
                    print_ok("Pretend to kill :"+vm)
                #fi
        #rof
        print_info("To kill all nonresponding VMs ->")
        for hadd in haddrd.keys():
            kill_nr_vms(haddrd[hadd])









if __name__ =='__main__':
    main()
