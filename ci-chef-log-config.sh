#!/bin/bash
mv /etc/chef/client.rb /etc/chef/client.rb_
sed "s/STDOUT/\"\/log.txt\"/g" /etc/chef/client.rb_ > /etc/chef/client.rb
chef-client
