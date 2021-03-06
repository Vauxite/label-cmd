#!/usr/bin/python
from deluge_client import DelugeRPCClient
import os,sys,json,subprocess,logging,shlex,re
class label_cmd:
    actions ={}
    labels ={}
    def read_config(self,path):
        with open(path+'') as json_data_file:
            data = json.load(json_data_file)
        return data
    def add_action(self,action,run):
		self.actions[action] = run
    def add_label(self,label,action):
        self.labels[label] = action
    def __init__(self,torrent_id, config_path,secret_path):
        self.config        	= self.read_config(config_path)
        self.secrets       	= self.read_config(secret_path)
        self.client 		=  DelugeRPCClient(self.config['deluge']['host'], self.config['deluge']['port'], self.secrets['deluge']['user'], self.secrets['deluge']['passwd'])
        self.client.connect()
        self.torrent       	= self.client.call('core.get_torrent_status', torrent_id, ['name','label','move_completed_path'])
        for action_file in self.config['config']['actions']['files']:
            file_data = self.read_config(action_file)
            for action in file_data:
                executable  = file_data[action]['executable']
                argument    = file_data[action]['arguments']
                self.add_action(action,{"executable":executable,"argument":argument})
        for label_file in self.config['config']['labels']['files']:
            file_data = self.read_config(label_file)
            for label in file_data:
                action = file_data[label]['action']
                self.add_label(label,action)
				
    def do_log(self,level,msg):
        logger = logging.getLogger('label-cmd')
        logger.setLevel(self.config['logging']['loglevel'])
                        
        handler = logging.FileHandler(self.config['logging']['logfile'])
        handler.setLevel(self.config['logging']['loglevel'])
        logformat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
        handler.setFormatter(logformat)

        logger.addHandler(handler)

        level = int(level)
        if level == 0:
            logger.info(msg)
        elif level == 1:
            logger.warn(msg)
        elif level == 2:
            logger.error(msg)
        elif level == 3:
            logger.debug(msg)
        else:
            raise
    def do_translate(self,arg):
		torrent = self.torrent
		for key,values in self.config['translate'].items():
			searchword = key
			replacewith = ''
			if isinstance(values,list):
				searchword = key
				for y in values:
					if y in torrent:
						replacewith += torrent[y]
					else:
						replacewith += y
			elif values in torrent:
				replacewith = torrent[values]
			else:
				self.do_log(2,"Error unsupported keyValue for torrent: " +key)
				
			arg = arg.replace(searchword,replacewith)
		return arg
    def get_label(self,torrent):
		try:
			label_name = torrent['label']
		except KeyError:
			label_name = "Default"
		if label_name in self.labels:
			return label_name
		else:
			self.do_log(1,"Unkown label '" + label_name +"'")
			return None
    def do_action(self):
		config = self.config
		label = self.get_label(self.torrent)
		if label is None:
			self.do_log(3,"Resorting to default action")
			label = 'Default'
		actions = self.labels[label]
		#
		if 'none' in actions:
			self.do_log(1,"Torrent '{0}' does not have any action".format(self.torrent['name']))
			return False
		for task in actions:
			#Get executable file
			executable = self.actions[task]['executable']
			#Get all arguments
			arguments = self.do_translate(self.actions[task]['argument'])
			
			cmd = executable +" "+ arguments
			
			process_call = shlex.split(cmd)

			
			result = subprocess.call(process_call,shell=False)

			if result == 0:
				self.do_log(0,"Succesfully executed task '{0}' for torrent '{1}'".format(task,self.torrent['name']))
			else:
				self.do_log(2,"Task '{0}' for torrent '{1}' exited with code '{2}'".format(task,self.torrent['name'],result))
		return True


#Set working directory to current directory
os.chdir(os.path.dirname(sys.argv[0]))

Torrent_Id      = sys.argv[1]
config_path     = "config/config.json"
secret_path     = "config/secrets.json"



c = label_cmd(Torrent_Id,config_path, secret_path)
c.do_action()




                    

