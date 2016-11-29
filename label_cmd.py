from deluge_client import DelugeRPCClient
import sys,json,subprocess,logging

class label_cmd:
    actions =[]
    labels ={}
    def read_config(self,path):
        with open(path+'') as json_data_file:
            data = json.load(json_data_file)
        return data
    def add_action(self,action,run):
        self.actions.append((action,run))
    def add_label(self,label,action):
        self.labels[label] = action
    def __init__(self,torrent, config_path,secret_path):
        self.torrent       = torrent
        self.config        = self.read_config(config_path)
        self.secrets       = self.read_config(secret_path)
        self.client =  DelugeRPCClient(self.config['deluge']['host'], self.config['deluge']['port'], self.secrets['deluge']['user'], self.secrets['deluge']['passwd'])
        self.client.connect()
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
    def do_log(level,msg):
        logger = logging.getLogger('label-cmd')
        logger.setLevel(config['logging']['loglevel'])
                        
        handler = logging.FileHandler(config['logging']['logfile'])
        handler.setLevel(config['logging']['loglevel'])
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
        for key,values in config['translate'].items():
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
                do_log(2,"Error unsupported keyValue for torrent: " +key)
            arg = arg.replace(searchword,replacewith)
        return arg
    def do_action(self):
        action = config['actions'][config['labels'][torrent['label']]['action']]
        executable = action['executable']
        arguments = do_translate(action['arguments'],torrent)
        
        cmd = executable + arguments
        result = subprocess.call(cmd)
        
        return result


Torrent_Id      ="0ccba3bc32bb5452bd700a39214e416414e6404f" #sys.argv[1]
config_path     = "config/config.json"
secret_path     = "config/secrets.json"
c = label_cmd(Torrent_Id,config_path, secret_path)

###Running the software
##if  len(sys.argv) > 2:
##    do_log(2,"Unsupported amount of arguments("+str(len(sys.argv))+"). Correct usage: script.py torrent_id")
##    sys.exit()
##else:
##    client =  DelugeRPCClient(config['deluge']['host'], config['deluge']['port'], secrets['deluge']['user'], secrets['deluge']['passwd'])
##    client.connect()
##    T_filter = ['name','label']
##    for value in config['translate'].values():
##        if isinstance(value,list):
##            for item in value:
##                T_filter.append(item) 
##        else:
##            T_filter.append(value)
##    torrent = client.call('core.get_torrent_status', Torrent_Id, T_filter)
##    if torrent['label'] in config['labels']:
##        try:
##            do_log(0,do_action(config,torrent))
##        except WindowsError:
##            do_log(2,"Windows is not supported")
##        except subprocess.CalledProcessError:
##            do_log(1,"Attempted action is not supported")
##        except:
##            do_log(2,"Unexpected error")
##            raise
##    else:
##        do_log(1,"Unkown label ("+torrent['label']+"). No Action taken")



                    

