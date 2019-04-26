"""
lumberjack.py
A plugin that will call a function whenever an agent checks in

INSTALLATION:
    cp lumberjack.py empire/plugins

USAGE (In empire):
    plugin lumberjack
"""

import requests
import functools
from lib.common.plugins import Plugin
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
        if len(args) != 2:
            print('usage: search <team#> <hostname>')
            return 1
        searchteam = args[0]
        searchhost = args[1]

        valid_agents = [] # Agents that match the search criteria
        

        for agent in agents:
            team_num = agent['internal_ip'].split('.')[1]
            if team_num == searchteam:
                if searchhost.lower() == agent['hostname'].lower():
                    if self.isAgentAlive(agent) == 'alive':
                        valid_agents.append(agent)
        
        
        valid_agents = sorted(valid_agents, key=lambda x:x['delay'])
        
        if valid_agents:
            print(helpers.color('[+] found agent {}'.format(valid_agents[0]['name'])))
            self.mainMenu.do_interact(valid_agents[0]['name'])
        else:
            print(helpers.color('[!] No agents alive found for ' +  searchteam + ' '+ searchhost) )


    def do_searchIP(self, args):
        """Interact with agent based on IP
        """
        agents = self.mainMenu.agents.get_agents_db()

        if not args.strip():
            print('usage: searchip <ip>')
            return 1
        ip = args

        valid_agents = []

        for agent in agents:
            if ip == agent['internal_ip']:
                valid_agents.append(agent)

        valid_agents = sorted(valid_agents, key=lambda x:x['delay'])

        if valid_agents:
            print(helpers.color('[+] found agent {}'.format(valid_agents[0]['name'])))
            self.mainMenu.do_interact(valid_agents[0]['name'])
        else:
            print(helpers.color('[!] No agents alive found for ' + ip))




