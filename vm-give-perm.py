#!/usr/bin/python2


import os
import sys
import getopt

import ConfigParser

from rest_helper.rest_helper import *






class conf():
    M_PLAT=''
#    DOMAIN='zjcloud.net'
    ROLE='UserRole'
#    CLUSTER='Default'
#    TEMPLATE='tmp'
    SET_ALL=False
#    PERM=False

#    MAXLIST=10000
    CONFIG_FILE='conf_perm_vm.ini'







def gen_conf_file(filename):
    config=ConfigParser.RawConfigParser()
    config.add_section('CONF')
    config.set('CONF','M_PLAT',conf.M_PLAT)
#    config.set('CONF','DOMAIN',conf.DOMAIN)
#    config.set('CONF','CLUSTER',conf.CLUSTER)
#    config.set('CONF','TEMPLATE',conf.TEMPLATE)
    config.set('CONF','ROLENAME',conf.ROLE)
    config.set('CONF','SET_ALL',conf.SET_ALL)
#    config.set('CONF','PERM',conf.PERM)

    with open(filename,'wb') as configfile:
        config.write(configfile)
    print_info("Generating a NEW configuration file: "+filename)
    print_info("----------------------------------")
    print_info("[CONF]")
    print_info("M_PLAT   =\t"+conf.M_PLAT)
#    print_info("DOMAIN   =\t"+conf.DOMAIN)
#    print_info("CLUSTER  =\t"+conf.CLUSTER)
#    print_info("TEMPLATE =\t"+conf.TEMPLATE)
    print_info("ROLENAME =\t"+conf.ROLE)
    print_info("SET_ALL  =\t"+str(conf.SET_ALL))
#    print_info("PERM     =\t"+str(conf.PERM))
    print_info("----------------------------------")





def read_conf_file(filename,conf):
    config=ConfigParser.RawConfigParser()
    config.read(filename)
    configc=config
    try:
        conf.M_PLAT=configc.get('CONF','M_PLAT')
#        conf.DOMAIN=configc.get('CONF','DOMAIN')
#        conf.CLUSTER=configc.get('CONF','CLUSTER')
#        conf.TEMPLATE=configc.get('CONF','TEMPLATE')
        conf.ROLE=configc.get('CONF','ROLENAME')
        conf.CLONE=configc.getboolean('CONF','SET_ALL')
#        conf.PERM=configc.getboolean('CONF','PERM')
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
#    print_info("CLUSTER  =\t"+conf.CLUSTER)
#    print_info("TEMPLATE =\t"+conf.TEMPLATE)
    print_info("ROLENAME =\t"+conf.ROLE)
    print_info("SET_ALL  =\t"+str(conf.SET_ALL))
#    print_info("PERM     =\t"+str(conf.PERM))
    print_info("----------------------------------")






def usage():
    message='''
Usage: %s [OPTIONS.] VMs..
        -i| --ini conf-file      \t: the configuration file.
        -m| --m-plat m-plat      \t: the Target Rhev-M.
        -l| --file vmlistfile    \t: a file contain VM names,separated by newline.
        -R| --range SCHEMA       \t: Tmp:PREF00.
        -E| --ere ere-pattern    \t: Select VMs by ere-pattern.
        -g| --glob-pattern       \t: Select VMs by glob-pattern.
        -a| --all                \t: Select all VMs(if `-E|-g' was given ,this option will be ignored).
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
    return vmnlist



## rargs:=  PREFIX001-PREFIX102[+TMP2:PREFIX....]

def parse_vmrange_args(rargs):
    vmslist=[]
    rargl=rargs.split('+') ## PREFIX001-PREFIX101
    for rarg in rargl:
        if len(rarg)==0:
            print_err('VM Range')
            sys.exit(-2)
        #fi

        vmrange=rarg.split('-')
        if len(vmrange)!=2:
            print_err('VM Range')
            sys.exit(-2)
        #fi
        vmfrom=vmrange[0]
        vmto=vmrange[1]
        match_from=re.match(r"(\w+)(\d+)",vmrange[0])
        prefix_from=match_from.group(1)
        num_from=int(match_from.group(2))
        match_to=re.match(r"(\w+)(\d+)",vmrange[1])
        prefix_to=match_from.group(1)
        num_to=int(match_from.group(2))
        if prefix_from !=prefix_to:
            print_err('VM Range')
            sys.exit(-2)
        #fi
        vmname_l=gen_range_vms_list(prefix_to,num_from,num_to)
        vmslist.extend(vmname_l)
    #rof
    return vmslist



def main():

    try:
        opts,args=getopt.getopt(sys.argv[1:],'i:l:m:R:hdE:g:a',['ini=','file=','range=','m-plat=','help','remove','ere=','glob=','all'])
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
    toremove=False


    print_info("="*20)
    print_info("\t%s"%sys.argv[0])
    print_info("="*20)

    for o,a in opts:
        if o in ('-h','--help'):
            need_help=True
            usage()
            sys.exit(0)
        elif o in ('-i','--ini'):
            have_conf_file=True
            conf.CONFIG_FILE=a
            read_conf_file(conf.CONFIG_FILE,conf)
        elif o in ('-m','--m-plat'):
            conf.M_PLAT=a
        elif o in ('-l','--file'):
            vm_listfile=a
        elif o in ('-R','--range'):
            vm_range=a
            conf.SET_ALL=False
        elif o in ('-E','--ere'):
            ere_pattern=a
            conf.SET_ALL=False
        elif o in ('-g','--glob'):
            glob_pattern=a
            conf.SET_ALL=False
        elif o in ('-a','--all'):
            conf.SET_ALL=True
        elif o in ('-d','--remove'):
            toremove=True
        else:
            usage()
            sys.exit(1)
    #rof



    print_info("conf.M_PLAT   : "+str(conf.M_PLAT))
    print_info("conf.ROLE     : " +str(conf.ROLE))
    print_info("conf.SET_ALL  : " +str(conf.SET_ALL))


    vm_givep_fail_list=[]

    vmslist=args

    if vm_range != '':
        vmslist.extend(parse_vmrange_args(vm_range))
    ##

    ipt=Mhm2Mip(conf.M_PLAT)
    Mipp=gen_ip(ipt)
    print_ok(Mipp)


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

#    for vm in keys:
#        vmid=vm2id_d[vm]
#        pname=vm
#        if not toremove:
#            if not vm_give_permission(Mipp,vmid,pname):
#                vm_givep_fail_list.append(vm)
#            #fi
#        else:
#            if not vm_remove_permissions(Mipp,vmid):
#                vm_givep_fail_list.append(vm)
#            #fi
#        #fi
#    #rof


    if not toremove:#give perms
        for vm in keys:
            vmid=vm2id_d[vm]
            pname=vm
            if not vm_give_permission(Mipp,vmid,pname):
                vm_givep_fail_list.append(vm)

    else: # remove perms
        for vm in keys:
            vmid=vm2id_d[vm]
            pname=vm
            if not vm_remove_permissions(Mipp,vmid):
                vm_givep_fail_list.append(vm)

    #fi




    if len(vm_givep_fail_list)!=0:
        print_warn('=====================')
        print_warn(vm_givep_fail_list)
    else:
        print_ok("Give permission to VMs Finished")


    if need_help:
        usage()
    #fi





if __name__=='__main__':
    main()
