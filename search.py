"""
search.py
A plugin to search agents based on team or ip

INSTALLATION:
    cp search.py empire/plugins

USAGE (In empire):
    plugin search
"""

import requests
import functools
from lib.common.plugins import Plugin
import lib.common.helpers as helpers
from datetime import datetime


class Plugin(Plugin):
    description = "A plugin to feed session checkins to the pwnboard and Sawmill"

    def onLoad(self):
        """
        init variables at start
        """
        self.mainMenu = None

    def register(self, mainMenu):
        """ any modifications to the mainMenu go here - e.g.
        registering functions to be run by user commands """
        mainMenu.__class__.do_search = self.do_searchAgents
        mainMenu.__class__.do_searchip = self.do_searchIP
        self.mainMenu = mainMenu  # Save this object for later

    def isAgentAlive(self, agent):
	"""Check if an agent is alive"""
	stamp = agent['lastseen_time']
	jitter = agent['jitter']
	delay = agent['delay']

	delta = datetime.now() - datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")

	if delta.seconds > delay * (jitter + 1) * 5:
            return 'dead'
        elif delta.seconds > delay * (jitter + 1):
            return 'missing'
        else:
            return 'alive'

    def do_searchAgents(self, args):
        """Search for a specific agent
        """
        agents = self.mainMenu.agents.get_agents_db()

        args = args.split()

        if len(args) == 0:
            print('usage: search <team#> <hostname> <option>')
	    print('Options:')
	    print('-l 		List active agents')
            return 1
        searchteam = args[0]
        searchhost = args[1]
        lst = False
        if len(args) == 3:
            if args[2] == '-l':
                lst = True
        valid_agents = []  # Agents that match the search criteria

        for agent in agents:
            team_num = agent['internal_ip'].split('.')[1]
            if team_num == searchteam:
                if searchhost.lower() == agent['hostname'].lower():
                    if self.isAgentAlive(agent) == 'alive':
                        valid_agents.append(agent)

        valid_agents = sorted(valid_agents, key=lambda x: x['delay'])

        if lst:
            if valid_agents:
                print('Name	  	 IP			Hostname		Last Seen')
                print('---------	 ---------	        ----------              ---------------------')
                for agent in valid_agents:
                    print(agent['name'] + '	 ' + agent['internal_ip'] + ' 	' + agent['hostname'] + helpers.color('\t\t\t[+]' + agent['lastseen_time']))
            else:
                print(helpers.color('[!] No agents alive found for ' + searchteam + ' ' + searchhost))

            return 1

        if valid_agents:
            print(helpers.color('[+] found agent {}'.format(valid_agents[0]['name'])))
            self.mainMenu.do_interact(valid_agents[0]['name'])
        else:
            print(helpers.color('[!] No agents alive found for ' + searchteam + ' ' + searchhost))


    def do_searchIP(self, args):
        """Interact with agent based on IP
        """
        agents=self.mainMenu.agents.get_agents_db()

        if not args.strip():
            print('usage: searchip <ip>')
            return 1
        ip=args

        valid_agents=[]

        for agent in agents:
            if ip == agent['internal_ip']:
                valid_agents.append(agent)

        valid_agents=sorted(valid_agents, key=lambda x: x['delay'])

        if valid_agents:
            print(helpers.color('[+] found agent {}'.format(valid_agents[0]['name'])))
            self.mainMenu.do_interact(valid_agents[0]['name'])
        else:
            print(helpers.color('[!] No agents alive found for ' + ip))

