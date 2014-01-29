#!/usr/bin/python2


import os
import sys
import getopt

import ConfigParser

from rest_helper.rest_helper import *






class conf():
    M_PLAT=''
    DOMAIN='zjcloud.net'
    ROLE='UserRole'
    CLUSTER='Default'
    TEMPLATE='tmp'
    NETWORK=''
    USB='Disable'
    CLONE=False
    PERM=False

    MAXLIST=10000
    CONFIG_FILE='conf_create_vm.ini'







def gen_conf_file(filename):
    config=ConfigParser.RawConfigParser()
    config.add_section('CONF')
    config.set('CONF','M_PLAT',conf.M_PLAT)
#    config.set('CONF','DOMAIN',conf.DOMAIN)
    config.set('CONF','CLUSTER',conf.CLUSTER)
    config.set('CONF','TEMPLATE',conf.TEMPLATE)
    config.set('CONF','NETWORK',conf.NETWORK)
    config.set('CONF','USB',conf.USB)
    config.set('CONF','ROLENAME',conf.ROLE)
    config.set('CONF','CLONE',conf.CLONE)
    config.set('CONF','PERM',conf.PERM)

    with open(filename,'wb') as configfile:
        config.write(configfile)
    print_info("Generating a NEW configuration file: "+filename)
    print_info("----------------------------------")
    print_info("[CONF]")
    print_info("M_PLAT   =\t"+conf.M_PLAT)
#    print_info("DOMAIN   =\t"+conf.DOMAIN)
    print_info("CLUSTER  =\t"+conf.CLUSTER)
    print_info("TEMPLATE =\t"+conf.TEMPLATE)
    print_info("NETWORK  =\t"+conf.NETWORK)
    print_info("USB      =\t"+conf.USB)
    print_info("ROLENAME =\t"+conf.ROLE)
    print_info("CLONE    =\t"+str(conf.CLONE))
    print_info("PERM     =\t"+str(conf.PERM))
    print_info("----------------------------------")





def read_conf_file(filename,conf):
    config=ConfigParser.RawConfigParser()
    config.read(filename)
    configc=config
    try:
        conf.M_PLAT=configc.get('CONF','M_PLAT')
#        conf.DOMAIN=configc.get('CONF','DOMAIN')
        conf.CLUSTER=configc.get('CONF','CLUSTER')
        conf.TEMPLATE=configc.get('CONF','TEMPLATE')
        conf.USB=configc.get('CONF','USB')
        conf.NETWORK=configc.get('CONF','NETWORK')
        conf.ROLE=configc.get('CONF','ROLENAME')
        conf.CLONE=configc.getboolean('CONF','CLONE')
        conf.PERM=configc.getboolean('CONF','PERM')
    except Exception as err:
        print_err("Read Configuration File")
        print err
        sys.exit(-1)
    #yrt
    print_info("Reading configurations from file :"+filename)
    print_info("----------------------------------")
    print_info("[CONF]")
    print_info("M_PLAT   =\t"+conf.M_PLAT)
#    print_info("DOMAIN   =\t"+conf.DOMAIN)
    print_info("CLUSTER  =\t"+conf.CLUSTER)
    print_info("TEMPLATE =\t"+conf.TEMPLATE)
    print_info("USB      =\t"+conf.USB)
    print_info("NETWORK  =\t"+conf.NETWORK)
    print_info("ROLENAME =\t"+conf.ROLE)
    print_info("CLONE    =\t"+str(conf.CLONE))
    print_info("PERM     =\t"+str(conf.PERM))
    print_info("----------------------------------")






def usage():
    message='''
Usage: %s [OPTIONS.] VMs..
        -i| --ini conf-file      \t: the configuration file.
        -m| --m-plat m-plat      \t: the Target Rhev-M.
        -l| --file vmlistfile    \t: a file contain VM names,separated by newline.
        -T| --template Template  \t: template name.
        -R| --range SCHEMA       \t: Tmp:PREF0X-PREF0Y
        -P| --give-perm          \t: give VMs corresponding permissions.
        -C| --cluster Cluster    \t: Cluster name.
        -c| --clone              \t: clone disks.
        -h| --help               \t: print this message..
'''%sys.argv[0]
    print message


def gen_list_from_re(olist,reg):
    nlist=[]
    for nd in olist:
        if re.match(reg,nd):
            nlist.append(nd)
        #fi
    #rof
    return nlist




def gen_range_vms_list(prefix,from_,to_):

    width=len(str(to_))
    vmnlist=[]
    num=from_
    while num<=to_:
        vmn=prefix+str(num).zfill(width)
        vmnlist.append(vmn)
        num+=1
    #elihw
    print_warn(vmnlist)
    return vmnlist



## rargs:=  TMP:PREFIX001-PREFIX102[+TMP2:PREFIX....]

def parse_range_args(rargs):
#    print_warn("================="+rargs)
    tvmslist=[]
    rargl=rargs.split('+') ## TMP:PREFIX001-PREFIX101
#    print_err(rargl)
    for rarg in rargl:
        rargg=rarg.split(':')
#        if len(rargg)!=2 or len(rargg[0])==0 or len(rargg[1])==0:
#            print_err('VM Range')
#            sys.exit(-2)
#        #fi
        if len(rargg)==1 and conf.TEMPLATE!='':
            template=conf.TEMPLATE
            vmrange=rargg[0].split('-')
        elif len(rargg)==2:
            template=rargg[0]
            vmrange=rargg[1].split('-')
        else:
            print_err("No Template given!")
            sys.exit(-2)
        #fi
        if len(vmrange)!=2:
            print_err('VM Range-3')
            sys.exit(-2)
        #fi
        vmfrom=vmrange[0]
        vmto=vmrange[1]
        match_from=re.match(r"([A-z]+)(\d+)",vmfrom)
        prefix_from=match_from.group(1)
        num_from=int(match_from.group(2))
        match_to=re.match(r"([A-z]+)(\d+)",vmto)
        prefix_to=match_to.group(1)
        num_to=int(match_to.group(2))
        print_info(prefix_from)
        print_info(prefix_to)

        if prefix_from !=prefix_to:
            print_err('VM Range-4')
            sys.exit(-2)
        #fi
        print_ok("From: "+str(num_from))
        print_ok("To  : "+str(num_to))
        vmname_l=gen_range_vms_list(prefix_to,num_from,num_to)
        list_len=len(vmname_l)
        tmp_l=[template]*list_len
        tvmslist.extend(zip(tmp_l,vmname_l))
    #rof
    return tvmslist



def main():

    try:
        opts,args=getopt.getopt(sys.argv[1:],'i:u:n:l:T:R:C:chm:',['ini=','file=','template=','usb=','net=','range=','give-perm','cluster=','clone','help','--m-plat'])
    except getopt.GetoptError as err:
        print_err(err)
        usage()
    #yrt
    print_info(args)


    vm_range=''
    vm_listfile=''


    need_help=False
    have_conf_file=False
    if not os.path.exists(conf.CONFIG_FILE):
        gen_conf_file(conf.CONFIG_FILE)
        print_info('Config-file: '+conf.CONFIG_FILE+' generated!!')
        sys.exit(0)
    else:
        read_conf_file(conf.CONFIG_FILE,conf)
    #fi
    ere_pattern=''
    glob_pattern=''
    vmlist=args[:]


    print_info("="*20)
    print_info("\t%s"%sys.argv[0])
    print_info("="*20)

    for o,a in opts:
        if o in ('-h','--help'):
            need_help=True
        elif o in ('-i','--ini'):
            have_conf_file=True
            conf.CONFIG_FILE=a
            read_conf_file(conf.CONFIG_FILE,conf)
        elif o in ('-m','--m-plat'):
            conf.M_PLAT=a
        elif o in ('-l','--file'):
            vm_listfile=a
        elif o in ('-T','--template'):
            conf.TEMPLATE=a
        elif o in ('-R','--range'):
            vm_range=a
        elif o in ('-P','--give-perm'):
            conf.PERM=True
        elif o in ('-C','--cluster'):
            conf.CLUSTER=a
        elif o in ('-c','--clone'):
            conf.CLONE=True
        elif o in ('-n','--net'):
            conf.NETWORK=a
        elif o in ('-u','--usb'):
            conf.USB=a
        else:
            usage()
            sys.exit(1)
    #rof



    print_info("conf.M_PLAT   : "+str(conf.M_PLAT))
    print_info("conf.CLUSTER  : " +str(conf.CLUSTER))
    print_info("conf.DOMAIN   : " +str(conf.DOMAIN))
    print_info("conf.ROLE     : " +str(conf.ROLE))
    print_info("conf.TEMPLATE : " +str(conf.TEMPLATE))
    print_info("conf.NETWORK  : " +str(conf.NETWORK))
    print_info("conf.USB      : " +str(conf.USB))
    print_info("conf.CLONE    : " +str(conf.CLONE))
    print_info("conf.PERM     : " +str(conf.PERM))



    tvmslist=[]
    vmslist=args

    vmlist_len=len(vmslist)
    temp_l=[conf.TEMPLATE]*vmlist_len

    tvmslist.extend(zip(temp_l,vmslist))

    if vm_range != '':
        tvmslist.extend(parse_range_args(vm_range))
    ##

    ipt=Mhm2Mip(conf.M_PLAT)
    mlink=gen_ip(ipt)

    vm_create_fail_list=[]
    for tpvm in tvmslist:
        if conf.CLONE==True:
            Clone='true'
        else:
            Clone='false'
        #fi
        vmn=tpvm[1]
        tpn=tpvm[0]
        if conf.USB=='Disable' or conf.USB=='':
            eusb='false'
            conf.USB=''
        else:
            eusb='true'
        #fi
#-----------
        vmid=vm_create(mlink,tpvm[1],tpvm[0],cluster=conf.CLUSTER,vlan=conf.NETWORK,clone=Clone,usb=eusb,usbtype=conf.USB)
        if vmid is None:
            vm_create_fail_list.append(tpvm[1])
        else:
            if conf.PERM:
                vm_give_permission(mlink,vmid,vmn)
        print tpvm
            #fi
        #fi

    print_warn('=====================')
    print_warn(vm_create_fail_list)


    if need_help:
        usage()
    #fi





if __name__=='__main__':
    main()
