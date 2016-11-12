import paramiko
import sys, os
import getpass
from fabric.api import local
#print 'sys.argv[0] =', sys.argv[0]
    #pathname = os.path.dirname(sys.argv[0])
    #print 'path =', pathname
    #print os.path.abspath(sys.argv[0])
me=getpass.getuser()
user='dino'
password='passw'
hostname = '52.90.173.220'
print type(hostname)
ip=hostname
myuser   = 'ec2-user'
mySSHK   = '/home/ddaniel/awssshkeypairh13m07s06.pem'
sshcon   = paramiko.SSHClient()  # will create the object
sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())# no known_hosts error
sshcon.connect(ip, username=myuser, key_filename=mySSHK) # no passwd needed
stdin, stdout, stderr = sshcon.exec_command('sudo useradd dino')
print stdout.readlines()
sshcon.close()
