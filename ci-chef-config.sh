#!/bin/bash
cat << EOF > /root/knife-configure.sh
#!/usr/bin/expect
set hostname [exec hostname]

spawn knife configure -i

expect -re "the config file?"
sleep 1
send "/root/.chef/knife.rb\r"

expect -re "chef server URL:"
sleep 1
send "http://61.43.139.121:4000\r"

expect -re "new client:"
sleep 1
send "\$hostname\r"

expect -re "admin clientname:"
sleep 1
send "\r"

expect -re "private key:"
sleep 1
send "\r"

expect -re "validation clientname:"
sleep 1
send "\r"

expect -re "validation key:"
sleep 1
send "\r"

expect -re "(or leave blank)"
sleep 1
send "\r"

expect -re "file written to"
sleep 1
send "\r"

interact
EOF

#- expect -c "spawn knife configure -i \n" -c "expect -re \"the config file?\"" -c "send /root/.chef/knife.rb\n" -c "sleep 10" -c "expect -re \"chef server URL:\"" -c "send http://61.43.139.121:4000\n" -c "sleep 3" -c "expect -re \"new client:\"" -c "send [info hostname]\n" -c "expect -re \"admin clientname:\"" -c "send \n" -c "expect -re \"private key:\"" -c "send \n" -c "expect -re \"validation clientname:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "interact"
#- expect -c "spawn knife configure -i \n" -c "expect -re \"(Y/N)\"" -c "send Y\n" -c "expect -re \"the config file?\"" -c "send \n" -c "sleep 10" -c "expect -re \"chef server URL:\"" -c "send http://61.43.139.122:4000\n" -c "sleep 3" -c "expect -re \"new client:\"" -c "send chef-gluster-vm-m\n" -c "expect -re \"admin clientname:\"" -c "send \n" -c "expect -re \"private key:\"" -c "send \n" -c "expect -re \"validation clientname:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "expect -re \"validation key:\"" -c "send \n" -c "interact"
#- sed "s/STDOUT/\"\/log.txt\"/g" /etc/chef/client.rb > /etc/chef/client.rb
#- chef-client
