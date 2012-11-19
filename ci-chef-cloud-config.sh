#cloud-config
#apt_update: true
#apt_upgrade: true

packages:
- expect

runcmd:
- [pwd]
- [whoami]
- [sh,/root/chef-configure.sh]
#- [wget, "http://61.43.139.125", -O/root/index.html]
#- [rm,/root/.ssh/known_hosts]
#- expect -c "spawn scp root@61.43.139.122:/etc/chef/validation.pem /etc/chef" -c "sleep 3" -c "expect -re \"connecting (yes/no)?\"" -c "sleep 1" -c "send yes\n" -c "send exit\n" -c "expect -re \"password:\"" -c "sleep 1" -c "send openstack\n" -c "interact"
#- expect -c "spawn scp root@61.43.139.122:/etc/chef/webui.pem /etc/chef" -c "expect -re \"password:\"" -c "send openstack\n" -c "interact"
#- cd /root/.chef/
#- [pwd]
#- [ls,/etc/chef]
#expect -c "spawn knife configure -i" -c "expect -re \"Overwrite /root/.chef/knife.rb? (Y/N)\"" -c "send Y\n" -c "expect -re \"Please enter the chef server URL\:\"" -c "send http://61.43.139.122:4000"
- expect -c "spawn knife configure -i \n" -c "expect -re \"the config file?\"" -c "send /root/.chef/knife.rb\n" -c "sleep 10" -c "expect -re \"chef server URL:\"" -c "send http://61.43.139.121:4000\n" -c "sleep 3" -c "expect -re \"new client:\"" -c "send [info hostname]\n" -c "expect -re \"admin clientname:\"" -c "send \n" -c "expect -re \"private key:\"" -c "send \n" -c "expect -re \"validation clientname:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "interact"
#- expect -c "spawn knife configure -i \n" -c "expect -re \"(Y/N)\"" -c "send Y\n" -c "expect -re \"the config file?\"" -c "send \n" -c "sleep 10" -c "expect -re \"chef server URL:\"" -c "send http://61.43.139.122:4000\n" -c "sleep 3" -c "expect -re \"new client:\"" -c "send chef-gluster-vm-m\n" -c "expect -re \"admin clientname:\"" -c "send \n" -c "expect -re \"private key:\"" -c "send \n" -c "expect -re \"validation clientname:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "interact"
- chef-client
