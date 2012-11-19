#!/bin/bash
cat << EOF > /root/chef-configure.sh
#expect -c "spawn scp root@61.43.139.121:/etc/chef/validation.pem /etc/chef" -c "sleep 3" -c "expect -re \"connecting (yes/no)?\"" -c "sleep 1" -c "send yes\n" -c "continue\n" -c "expect -re \"password:\"" -c "sleep 1" -c "send openstack\n" -c "sleep 1" -c "interact"
expect -c "spawn scp root@61.43.139.121:/etc/chef/webui.pem /etc/chef" -c "expect -re \"password:\"" -c "send openstack\n" -c "sleep 1" -c "interact"
expect -c "spawn scp root@61.43.139.121:/etc/chef/validation.pem /etc/chef" -c "expect -re \"password:\"" -c "send openstack\n" -c "sleep 1" -c "interact"
EOF

cat << EOF > /root/.ssh/config
Host 61.43.139.121
UserKnownHostsFile /dev/null
StrictHostKeyChecking no
EOF
