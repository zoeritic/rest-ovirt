#!/usr/bin/python2




import os
import sys
import re
import getopt
import time
import ConfigParser

from rest_helper.rest_helper import *




class conf():

    Total=0
    total=0
    EXPECT_STATES=['up','not_responding','wait_for_launch']
#    STATE_MASK=[]




def get_vms_info_from_vms_xml(vms_xml):#returned from /api/vms
    vmsdoc=etree.fromstring(vms_xml)
    vmnds=vmsdoc.findall('vm')
    vm_info_d={}
    for vm in vmnds:
        vmname=vm.find('name').text
        vmstate=vm.find('status').find('state').text
        vmusb=vm.find('usb').find('enabled').text
        vmoverride=vm.find('display').find('allow_override').text
        vm_info_d[vmname]=(vmstate,vmusb,vmoverride) #More TODO

    return vm_info_d


def get_host_info_from_hosts_xml(hosts_xml):
    hostsdoc=etree.fromstring(hosts_xml)
    hosts=hostsdoc.findall('host')
    host_info_d={}
    for h in hosts:
        hname=h.find('name').text
        hstate=h.find('status').find('state').text
        haddr=h.find('address').text
        host_info_d[hname]=(hstate,haddr) #More TODO
    
    return host_info_d


def get_storagedomain_info_from_xml(storagedomain_xml):
    sdsdoc=etree.fromstring(storagedomain_xml)
    sds=sdsdoc.findall('storage_domain')
    sd_info_d={}
    for sd in sds:
        sdname=sd.find('name').text
        sdstat_=sd.find('status')
        if sdstat_ is None:
            sdstat='OK'
        else:
            sdstat=sdstat_.find('state').text
        #fi
        sdmaster=sd.find('master').text
#        print_err("Master "+sdmaster)
        sdtype=sd.find('storage').find('type').text
        sdavail=sd.find('available').text
        sdused=sd.find('used').text
        sd_info_d[sdname]=(sdstat,sdmaster,sdtype,sdused,sdavail)

    return sd_info_d




def get_class_state_dict(vm_info_d):
    vm_class_d={}
    keys=vm_info_d.keys()
    keys.sort()
    for vm in keys:
        classre=re.match('([A-z]+[0-9])([0-9]+)',vm)
        if classre is None:
            continue
        classname=classre.group(1)
        vmstat=vm_info_d[vm][0]
        vl=vm_class_d.get(classname,[])
        if len(vl)==0:
            vm_class_d[classname]=[]
            vm_class_d[classname].append((vm,vmstat))
        else:
            vm_class_d[classname].append((vm,vmstat))
        #fi
    #rof
    return vm_class_d




def print_state_dict(vmclist,expect_states):
    stat_d={}
    instat=0
    for it in vmclist:
        vmname=it[0]
        vmstat=it[1]
        if not expect_states is None:
            if not vmstat in expect_states:
#                print_err(vmstat+")("+str(expect_states))
                continue
        else:#None
            pass
        #fi
        instat+=1
#        num=stat_d.get(vmstat,0)
        stat_d[vmstat]=stat_d.get(vmstat,0)+1
    for s in stat_d.keys():
        if s=='up':
            print ">>> \033[32m%10.8s\033[0m : %d "%(s,stat_d[s])
        elif s=='not_responding':
            print ">>> \033[31m%10.8s\033[0m : %d "%(s,stat_d[s])
        else:
            print ">>> \033[33m%10.8s\033[0m : %d "%(s,stat_d[s])
#    print_err(stat_d)    
    return instat



def print_hosts_storagedomains_info(host_info_d,sds_info_d):

    keys=host_info_d.keys()
    keys.sort()

    print "\033[36m===========================\033[0m"
    for it in keys:
        hstat=host_info_d[it][0]
        if not hstat=='up':
            print "\033[31m++ %5s : \033[4m%s \033[0m"%(it,hstat)
        else:
            print "\033[32m++ %5s\033[0m : %s \033[0m"%(it,hstat)
    
    if not sds_info_d is None:
        skeys=sds_info_d.keys()
        skeys.sort()
            

        print "++++++++++++++++++++++++++++++"
#    print sds_info_d
        for it in skeys:
            sdstat=sds_info_d[it][0]
            sdmaster=sds_info_d[it][1]
            sdtype=sds_info_d[it][2]
            sdavail=sds_info_d[it][4]

            if sdstat=='OK':
                print "\033[32m++ %5s\033[0m : %s \033[0m"%(it,sdstat),
            elif sdstat=='unattached':
		#print_err('UNATTECHED %s: %s'%(it,sdstat))
                continue
            else:
                print "\033[31m++ %5s : \033[4m%s \033[0m"%(it,sdstat),
#            print "\033[32m++ %5s\033[0m : %s \033[0m"%(it,sdstat),
        #fi
            if sdmaster=='true':
                print "\033[33m master",
            if sdtype=='localfs':
                print " Local",
            print "\033[0m "

    #fi

    print "\033[36m===========================\033[0m"

def print_vm_class_dict(vm_class_d,expect_states):

    vmclass=vm_class_d.keys()
    vmclass.sort()
    Mtotal=0
    MTotal=0    

    print "\033[32m===========================\033[0m"
    for vmc in vmclass:
#        stat_d={}
        print "\033[36m>>\033[0m\033[1m::ClassName:\033[5m\033[40;33m%8s\033[0m ::<<"%vmc
        vmclist=vm_class_d[vmc]
        Total=len(vmclist)
        instat=print_state_dict(vmclist,expect_states)
        print "\033[40;36m>> Total : %d (of %d ) \033[0m"%(instat,Total)
        print "\033[32m---------------------------\033[0m"
        Mtotal+=instat
        MTotal+=Total
    return (Mtotal,MTotal)



def print_M_info(Mhn,expect_states,need_storage):

    Mip=Mhm2Mip(Mhn)
    Mipp=gen_ip(Mip)
    vms_xml=list_all_vms_xml(Mipp)
    hosts_xml=list_all_hosts_xml(Mipp)
    if need_storage:
        sds_xml=list_all_storagedomains_xml(Mipp)    
        sds_info=get_storagedomain_info_from_xml(sds_xml)
    #fi
    hosts_info=get_host_info_from_hosts_xml(hosts_xml)
    vms_info=get_vms_info_from_vms_xml(vms_xml)
    #print_err( sds_info)

    vm_class=get_class_state_dict(vms_info)
    print "\033[35m\033[1m>>>:%s:=[%s]<<<<<<\033[0m"%(Mhn,Mipp)
#    print Mipp
    if not need_storage:
        sds_info=None
    print_hosts_storagedomains_info(hosts_info,sds_info)
    mt,mT=print_vm_class_dict(vm_class,expect_states)
    conf.Total+=mT
    conf.total+=mt
    print "\033[1m\033[40;32m==TOTAL: %d of %d VMs in %s \033[0m"%(mt,mT,Mhn)

 


def usage():

    message='''

Usage: %s [OPTIONS.] Mhostname...

        -s | --state expect_state  \t: VMs with expect_state will be statisticed.
        -a | --all                 \t: 
        -U | --up                  \t:
        -D | --down                \t:
        -W | --wait-for-launch     \t:
        -O | --other-state         \t:
        -S | --storage             \t:
        -T | --t-m                 \t: Default is not set.
        -h | --help                \t: print this message.
'''%sys.argv[0]
    print message





def main():

    try:
        opts,args=getopt.getopt(sys.argv[1:],"s:ShaAUDWNOT",['all','help','state=','up','storage','all-states','down','not-responding','wait-for-launch','other-state','t-m'])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(3)
    #yrt
    
#    state_masks=conf.STATE_MASK

    show_storage=False

    expect_states=[]

    if len(args)==0:
        mhost_list=gc.MS_LIST
    else:
        mhost_list=args[:]
        print_info("Mhost list from argvs: "+str(mhost_list))
    #fi
    for o,a in opts:
        if o in ('-s','--state'):
            expect_states.append(a)
        elif o in ('-h','--help'):
            need_help=True
            usage()
            sys.exit(0)
        elif o in ('-a','--all'):
            mhost_list=gc.MS_LIST
        elif o in ('-A','--all-states'):
            expect_states=None
        elif o in ('-S','--storage'):
            show_storage=True
        elif o in ('-U','--up'):
            expect_states.append('up')
        elif o in ('-D','--down'):
            expect_states.append('down')
        elif o in ('-W','--wait-for-launch'):
            expect_states.append('wait_for_launch')
        elif o in ('-N','--not-responding'):
            expect_states.append('not_responding')
        elif o in ('-T','-t-m'):
            mhost_list=gc.MH_LIST
        elif o in ('-O','--other-state'):
            pass    
        else:
            usage()
            sys.exit(2)
        #fi

    print_ok("RhevM to be monitor.> "+str(mhost_list))
    
    if len(expect_states)==0:
        expect_states=conf.EXPECT_STATES
    

    for mhost in mhost_list:    
        print_M_info(mhost,expect_states,show_storage)

    print_ok(" VM total : %d / Total:%d "%(conf.total,conf.Total))
    print_ok(" %s"%time.ctime())

if __name__ == '__main__':
    main()


#gen_ip('')
#ip='182'
#Mipp=gen_ip(ip)


#vms_xml=list_all_vms_xml(Mipp)

#hosts_xml=list_all_hosts_xml(Mipp)
#hosts_info=get_host_info_from_hosts_xml(hosts_xml)


#vm_info=get_vms_info_from_vms_xml(vms_xml)

#vm_class=get_class_state_dict(vm_info)

#print_hosts_info(hosts_info)
#print_vm_class_dict(vm_class)
#print_info(vm_class)



