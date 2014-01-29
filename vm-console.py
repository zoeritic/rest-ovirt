#!/usr/bin/python2

import sys
import os
import urllib
import ConfigParser
import getopt
import shutil

from  rest_helper.rest_helper import *



class conf():
    M_PLAT=''
    DOMAIN=''
    USER=''
    PASSWD=''

    FULL_SCREEN=True
    CONFIG_FILE='conf_vm_console.ini'
    CERTS_DIR='.certs/'
    PERM_PATH=' ~/.spicec/spice_truststore.pem'

    CONSOLE='spicy'


def gen_conf(filename=conf.CONFIG_FILE):
    config=ConfigParser.RawConfigParser()
    config.add_section('CONNECTION')
    config.set('CONNECTION','M_PLAT',conf.M_PLAT)
    config.set('CONNECTION','DOMAIN',conf.DOMAIN)
    config.set('CONNECTION','USER',conf.USER)
    config.set('CONNECTION','PASSWD',conf.PASSWD)
    fd=open(filename,'wb')
    config.write(fd)
    print_info('A NEW Configuration File Generated!')
    print_info("M_PLAT  =\t"+conf.M_PLAT)
    print_info("DOMAIN  =\t"+conf.DOMAIN)
    print_info("USER    =\t"+conf.USER)
    print_info("PASSWD  =\t"+conf.PASSWD)

def read_conf(filename,conf):
    configc=ConfigParser.RawConfigParser()
    configc.read(filename)
    conf.M_PLAT=configc.get('CONNECTION','M_PLAT')
    conf.DOMAIN=configc.get('CONNECTION','DOMAIN')
    conf.USER=configc.get('CONNECTION','USER')
    conf.PASSWD=configc.get('CONNECTION','PASSWD')
    print_info("======================")
    print_info("M_PLAT  =\t"+conf.M_PLAT)
    print_info("DOMAIN  =\t"+conf.DOMAIN)
    print_info("USER    =\t"+conf.USER)
    print_info("PASSWD  =\t"+conf.PASSWD)



def get_ca_crt(Mipp):
#	Mipp='https://'+ip+':8443'
    URL=Mipp+'/ca.crt'
    page=urllib.urlopen(URL)
    crt=page.read()
    print crt
    ip=Mipp[8:-5]
    crt_file=conf.CERTS_DIR+ip+'_ca.crt'
    f=open(crt_file,'w')
    f.write(crt)
    f.close()
#    shutil.copyfile(crt_file,conf.PERM_PATH)

    syscmd=' /usr/bin/cp '+crt_file+conf.PERM_PATH
    print_info(syscmd)
    rt=os.system(syscmd)
    if rt!=0:
        print_err("Copy Cert_File Failed")
    print_ok("certification saved in [%s]"%crt_file)
    return crt_file






def get_vm_info(Mipp,vmname):
#    print_warn(Mipp+' '+vmname)
    rt_xml=get_vms_by_name_xml(Mipp,vmname)
    doc=etree.fromstring(rt_xml)
    vmid=doc.find('vm').attrib['id']

    vm_info_d={}
    res=Mipp+'/api/vms/'+vmid
    rt_xml=rest_request(res,'GET')
#   print_info(rt_xml)
    vmnode=etree.fromstring(rt_xml)
#   vmnode=doc.find('vm')
    print_info(vmnode)
    display_nd=vmnode.find('display')
    host_ip=display_nd.find('address').text
    host_port=display_nd.find('port').text
    host_sport=display_nd.find('secure_port').text
    host_cert_subject=display_nd.find('certificate').find('subject').text
    domain=vmnode.find('domain').find('name').text
    vm_info_d['vm']=vmname
    vm_info_d['id']=vmid
    vm_info_d['host']=host_ip
    vm_info_d['port']=host_port
    vm_info_d['sport']=host_sport
    vm_info_d['domain']=domain
    vm_info_d['host_cert_subject']=host_cert_subject
    return vm_info_d


def viewer_open(M,vmname,C,user=gc.USER,passwd=gc.PASSWD,options=None):

    f4=Mhm2Mip(M)
    Mipp=gen_ip(f4)
    cert_file=get_ca_crt(Mipp)
    vm_info_d=get_vm_info(Mipp,vmname)
    vmid=vm_info_d['id']
    host=vm_info_d['host']
    port=vm_info_d['port']
    sport=vm_info_d['sport']
    host_cert_subject=vm_info_d['host_cert_subject']

    print_warn("::"+user+" :: "+passwd)
    #ticket_d=vm_set_ticket(Mipp,vmid)
    ticket_d=vm_set_ticket(Mipp,vmid,user,passwd)

    if ticket_d['state']!='complete':
        print_err("Set Ticket for VM: "+vmname)
        sys.exit(-1)
    #fi
    passwd=ticket_d['ticket_value']

    if C=='remote-viewer':
	CMD='''remote-viewer --spice-ca-file=%(cert_file)s --spice-host-subject '%(subject)s' spice://%(host)s/?port=%(port)s\&tls-port=%(sport)s\&password=%(passwd)s '''%{'cert_file':cert_file,'subject':host_cert_subject,'host':host,'port':port,'sport':sport,'passwd':passwd}
    elif C=='spicy':
	CMD='''spicy -h %(host)s -s %(sport)s  -w %(passwd)s '''%{'host':host,'sport':sport,'passwd':passwd}
    else:
        CMD='echo WRONG VIEWER!!'
    #fi
    if conf.FULL_SCREEN:
        CMD=CMD+" "+"-f "
    #fi
    if not options is None:
        CMD=CMD+" "+options
    #fi
    print_ok(CMD)
    rv=os.system(CMD)


def usage():
    message='''

Usage %s [OPTION.] VM
        -i | --ini            \t: Configuration File.
        -m | --m-plat M       \t: Set the Rhevm name.
        -l | --address ip     \t: ip of RhevM.
        -u | --usr loginname  \t: User name for Login.
        -p | --password PASSWD\t: Password with user.
        -f | --full           \t: Open Console full screen.
        -h | --help           \t: Print this Message.

for Rhevm 3.1 or Ovirt 3.1
3.2 not suitable[vm_set_ticket]
'''%argv[0]
    print message




def main():
    try:
        opts,args=getopt.getopt(sys.argv[1:],'m:l:fhi:c:SRu:p:',['m-plat=','address=','full','help','ini=','console=','spicy','remote-viewer','user=','password='])
    except getopt.GetoptError as err:
        print_err(err)
        usage()
    #yrt


    if not os.path.exists(conf.CONFIG_FILE):
        gen_conf(conf.CONFIG_FILE)
        sys.exit(0)
    else:
        read_conf(conf.CONFIG_FILE,conf)
    #fi

    VMs=args[:]
    if len(VMs)==0:
        print_info("No VM was given..")
        sys.exit(-1)
    elif len(VMs)!=1:
        print_info("More than One VM was given,Only the First VM will Open..")
        sys.exit(-2)
    #fi
    VM=VMs[0]
    print_info(VM)

    from_ini=True
    RMip=''

    for o,a in opts:
        if o in ('-m','--m-plat'):
            conf.M_PLAT=a
            from_ini=False
        elif o in ('-l','--adress'):
            RMip=a
            from_ini=False
        elif o in ('-i','--ini'):
            conf.CONFIG_FILE=a
        elif o in ('-u','--user'):
            conf.USER=a
        elif o in ('-p','--password'):
            conf.PASSWD=a
        elif o in ('-f','--full'):
            conf.FULL_SCREEN=True
        elif o in ('-c','--console'):
            conf.CONSOLE=a
        elif o in ('-S','--spicy'):
            conf.CONSOLE='spicy'
        elif o in ('-R','--remote-viewer'):
            conf.CONSOLE='remote-viewer'
        elif o in ('-h','--help'):
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(1)
	#fi
    #rof
    print_ok("======================")
    print_ok("M_PLAT  =\t"+conf.M_PLAT)
    print_ok("DOMAIN  =\t"+conf.DOMAIN)
    print_ok("USER    =\t"+conf.USER)
    print_ok("PASSWD  =\t"+conf.PASSWD)

    print_ok(gc.USER)
    print_ok(gc.PASSWD)

    viewer_open(conf.M_PLAT,VM,user=conf.USER,passwd=conf.PASSWD,C=conf.CONSOLE)



if __name__ == '__main__':
    main()

