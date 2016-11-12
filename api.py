#!/usr/bin/env python

from flask import Flask, request
from flask_restful import Resource, Api
from boto.manage.cmdshell import sshclient_from_instance
import paramiko
import sys, os
import getpass
from fabric.api import local
import time
from time import gmtime, strftime
import paramiko

# AWS module
import boto
from boto import ec2

app = Flask(__name__)
api = Api(app)

@app.route('/spawnssh', methods=['GET'])
def get_user():
   user = request.args.get('user')
   pwd = request.args.get('pwd')
   #return 'success', 200

#Connect to AWS instance
   aws_conn = ec2.connect_to_region("XXXXXX",
              aws_access_key_id='XXXXXXXXXX',
              aws_secret_access_key='XXXXXXXXXXXXX')

#Create sshkey and security group
   sessionStart = strftime("h%Hm%Ms%S", gmtime()) 
   keyPairName = "awssshkeypair" + sessionStart
   awsKeyPair = aws_conn.create_key_pair(keyPairName)
   awsKeyPair.save("~")
   securityGroupName = "awssshsecuritygroup" + sessionStart
   securityGroupDesc = "For access and analysis of programmatically spawned machines"
   awsSecGroup = aws_conn.create_security_group(securityGroupName, securityGroupDesc)
   awsSecGroup.authorize('tcp',22,22,'0.0.0.0/0')

#Launch New Instance
   vm=aws_conn.run_instances('ami-b73b63a0',
        instance_type='t2.micro',
	security_groups = [securityGroupName],
        key_name = keyPairName,
        max_count = 1,
        user_data = (""" #!/bin/bash 
                  sudo sed -i 's/PasswordAuthentication\ no/PasswordAuthentication\ yes/g' /etc/ssh/sshd_config
                  sudo /etc/init.d/sshd reload                             """)
   )
   print "New instance created"
  
# Get Instance IP Address
   demo = vm.instances[0]
   while demo.update () != 'running':
         time.sleep(1)
   ip = demo.ip_address
   print ip
   awshost=str(ip)
   print awshost
   print type(awshost)
   time.sleep(40)

# Add SSH User & Password
   me=getpass.getuser()
   awsuser  = 'ec2-user'
   mySSHK   = "/home/" + me + "/" + keyPairName +".pem"
   port = 22
   sshcon   = paramiko.SSHClient()  # will create the object
   sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())# no known_hosts error
   sshcon.connect(awshost, port, awsuser, key_filename=mySSHK) # no passwd needed
   adduser = 'sudo useradd' +' '+ user
   chpass  = 'sudo echo' +' '+ user + ':' + pwd +'| sudo chpasswd'
   stdin, stdout, stderr = sshcon.exec_command(adduser)
   stdin, stdout, stderr = sshcon.exec_command(chpass)
   print stdout.readlines()
   print stderr.readlines()
   sshcon.close()
   print "Use following IP address, and your username,password to ssh server"
   return ip,user
  
if __name__ == '__main__':
     app.debug = True
     app.run()
