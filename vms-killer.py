#!/usr/bin/python2
import os
import sys
import getopt
import ConfigParser
import threading
import subprocess
import re

from rest_helper.rest_helper import *

class conf():
    M_PLAT=''
    SET_ALL=False
    KILL=False
    KILL_NONRESP=False

    RE_VDSMD=False


#['h-p-13','h-p-14','h-p-15','h-p-16','h-p-17','h-p-18','h-p-19','h-p-20','h-p-21','h-p-22','h-p-23','h-p-24','h-p-29','h-p-30','h-p-31','h-p-32','h-p-33','h-p-34','h-p-35','h-p-36','h-p-37','h-p-38','h-p-39','h-p-40','h-p-41','h-p-42','h-p-43','h-p-44','h-p-45','h-p-46','h-p-47','h-p-48','h-p-49','h-p-50','h-p-51','h-p-52']

#['h-p-02','h-p-03','h-p-04','h-p-05','h-p-06','h-p-07','h-p-08','h-p-09','h-p-10','h-p-11','h-p-12','h-p-25','h-p-26','h-p-27','h-p-28']


def do_SSH(HIP,cmd='hostname',user='root',password='redhat'):
#    CMD='ssh '+user+'@'+HIP+' '+cmd

 #   cmd0='VMPID=$(vdsClient -s 0 list table|grep '+vmname+' |awk \"{print \\\$2}\") && test \'0\' -eq $(netstat -atnp|grep \\\$VMPID|grep ESTABLISHED |wc -l) && kill -9 \\\$VMPID'

    print_ok("H: "+HIP)
    print_ok('Executing: '+cmd)
    EXPECT_SSH_CMD='''
    expect  -c '
    set ip %(IP)s
    set password %(PASSWD)s
    set timeout 15
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





def get_vminfo(dossh):
    lines=dossh.split('\n')
    vds_d={}
    for l in lines:
        llst=l.split()
        if len(llst)==4:
            vm=llst[2]
            vmid=llst[0]
            vmpid=llst[1]
            vmstat=llst[3]
            print_ok(l)
            vds_d[vm]=[vmid,vmpid,vmstat]
#    print_ok(vds_d)
    return vds_d

def kill_vm_by_name(hip,vmname):
    CMD=r'VMPID=\$(vdsClient -s 0 list table|grep '+vmname+r' |awk \"{print \\\$2}\") && test \"0\" -eq \$(netstat -atnp|grep \$VMPID|grep ESTABLISHED |wc -l) && kill -9 \$VMPID '
#    CMD=r"vdsClient -s 0 list table |grep "+vmname+r' |awk \"{print \\\$2}\" |xargs kill -9 '
    rt=do_SSH(hip,CMD)
    #print_info(rt)


def kill_nr_vms(hip,state=r"\"Up\\*\""):
    CMD=r"vdsClient -s 0 list table |grep "+state+r' |awk \"{print \\\$2}\" |xargs kill -9 '
    rt=do_SSH(hip,CMD)
    print_info(rt)

def restart_vdsmd(hip,deep=False):
    if deep:
        CMD=r"service vdsmd restart&&initctl restart libvirtd&&service vdsmd start &"
    else:
        CMD=r"service vdsmd restart &"
    #fi
    rt=do_SSH(hip,CMD)
    print_info(rt)

#hlist=Mhm2Hhm(sys.argv[1])
#for h in hlist:
#    print   '10.11.4.'+Hhm2Hip(h)
#print "=="+Hhm2Hip(sys.argv[1])




#rt=do_SSH('10.11.4.91','vdsClient -s 0 list table')

#kill_vm_by_name('10.11.4.134','DKEZ501')
#kill_nr_vms('10.11.4.91')


def usage():
    message=u'''
Usage: %(pro)s [OPTION] VM1 VM2 ..

    -m | --m M          \t: specify the RhevM.
    -k | --kill         \t: enforce to kill the VMs which are selected.
    -g | --glob pattern \t: Select VMs by glob.
    -p | --prefix class \t: direct pass class to vdsm.
    -E | --ere pattern  \t: Select VMs by ERE.
    -a | --all          \t: Select all VMs.
    -r | --revdsmd H    \t: restart vdsmd .
    -n | --nonrespond   \t: kill all non responding VMs(Default).
    -h | --help         \t: Print this message.

.e.g:
    %(pro)s -m s-m01 -k -g YDJZX5*
        =>
    %(pro)s -m s-m14 -k -E T1[234]
        =>
    %(pro)s -m s-m14 -r h-p-01
        =>
    %(pro)s -m s-m14 -n
        =>
    %(pro)s -m s-m01 -k  YDJZX501 RSZX505
        =>


    '''%{"pro":sys.argv[0]}
    print message




def main():
    opts,args=getopt.getopt(sys.argv[1:],'m:hnE:g:kr:',['m-plat=','help','nonrespond','glob=','ere=','kill','revdsmd='])


    glob_pattern=''
    ere_pattern=''
    class_pre=''

    H_name=''
    re_deep=False

    for o,a in opts:
        if o in ('-m','--m-plat'):
            conf.M_PLAT=a
        elif o in ('-g','--glob'):
            glob_pattern=a
            conf.SET_ALL=False
        elif o in ('-E','--ere'):
            ere_pattern=a
            conf.SET_ALL=False
        elif o in ('-p','--prefix'):
            class_pre=a
            conf.SET_ALL=False
        elif o in ('-k','--kill'):
            conf.KILL=True
        elif o in ('-a','--all'):
            conf.SET_ALL=True
        elif o in ('-r'):
            conf.RE_VDSMD=True
            H_name=a.strip()
        elif o in ('--revdsmd'):
            conf.RE_VDSMD=True
            H_name=a.strip()
            re_deep=True
        elif o in ('-n','--nonrespond'):
            conf.KILL_NONRESP=True
        elif o in ('-h','--help'):
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(1)
        #fi

    if conf.RE_VDSMD:
        print_info("Going to Re start vdsmd..")
        print_info("Hostname: "+H_name)
        hip=gc.URL_PRE+Hhm2Hip(H_name)
        restart_vdsmd(hip,re_deep)
        print_ok("Bye..")
        sys.exit(1)


    vmlist=args

    ip=Mhm2Mip(conf.M_PLAT)
    Mipp=gen_ip(ip)

    vm2hip={}

    hmlist=Mhm2Hhm(conf.M_PLAT)


    if conf.KILL_NONRESP==True:
        print_info("To kill all Nonresponding VMs..")
        for ha in hmlist:
            haddr=gc.URL_PRE+Hhm2Hip(ha)
            print_info("  -=- "+haddr)
            kill_nr_vms(haddr)
        sys.exit(0)

    if conf.SET_ALL and glob_pattern!='' and ere_pattern!='' and len(vmlist)==0:
        rt_xml=list_all_vms_xml(Mipp)
        vm2hip=get_host_of_vms(rt_xml)
    elif glob_pattern!='' or ere_pattern!='' or class_pre!='':
        if glob_pattern!=''or class_pre!='':
            rt_xml=get_vms_by_name_xml(Mipp,glob_pattern)
            vm2hip=get_host_of_vms(rt_xml)
#            print_info(vm2hip)
        elif ere_pattern!='':
            rt_xml=list_all_vms_xml(Mipp)
            vm2hip=get_host_of_vms(rt_xml)
            for vmn in vm2hip.keys():
                if not re.match(ere_pattern,vmn):
                    vm2hip.pop(vmn)
    else:
        rt_xml=list_all_vms_xml(Mipp)
        vm2hip=get_host_of_vms(rt_xml)
        for vm in vm2hip.keys():
            if not vm in vmlist:
                del vm2hip[vm]

    #fi

    keys=vm2hip.keys()
    keys.sort()
    print_info(keys)
    for vm in keys:
        hip=vm2hip[vm][1]
        if conf.KILL==True:
            kill_vm_by_name(hip,vm)
            print_ok("VM: "+vm+" has been killed!!")
        else:
            print_ok("Pretend to kill :"+vm)
#            kill_vm_by_name(hip,vm)
        #fi




    print_ok("Bye..")



#print_info(rt)


if __name__=='__main__':
    main()
