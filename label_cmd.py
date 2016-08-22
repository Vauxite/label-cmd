from deluge_client import DelugeRPCClient
import sys,json,subprocess,logging
#Argv
##1 Script_file
##2 Torrent_Id

#for testing
#sys.argv = [sys.argv[0],'torrent HASH']



def readConfig(path):
    with open(path+'') as json_data_file:
        data = json.load(json_data_file)
    return data

config_path = "config/config.json"
secret_path = "config/secrets.json"

config = readConfig(config_path)
secrets = readConfig(secret_path)

Torrent_Id      = sys.argv[1]

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

def do_translate(arg,torrent):
    for key,values in config['core']['translate'].items():
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
def do_action(config,torrent):
    action = config['actions'][config['labels'][torrent['label']]['action']]
    executable = action['executable']
    arguments = do_translate(action['arguments'],torrent)
    
    cmd = executable + arguments
    result = subprocess.call(cmd)
    
    return result
def get_action(config,torrent):
    action = config['labels'][torrent['label']]['action']
    return config['actions'][action]
if  len(sys.argv) != 2:
    do_log(2,"Unsupported amount of arguments("+str(len(sys.argv))+"). Correct usage: script.py torrent_id")
    sys.exit()
else:
    client =  DelugeRPCClient(config['deluge']['host'], config['deluge']['port'], secrets['deluge']['user'], secrets['deluge']['passwd'])
    client.connect()
    T_filter = ['name','label']
    for value in config['core']['translate'].values():
        if isinstance(value,list):
            for item in value:
                T_filter.append(item) 
        else:
            T_filter.append(value)
    torrent = client.call('core.get_torrent_status', Torrent_Id, T_filter)
    if torrent['label'] in config['labels']:
        try:
            do_log(0,do_action(config,torrent))
        except WindowsError:
            do_log(2,"Windows is not supported")
        except subprocess.CalledProcessError:
            do_log(1,"Attempted action is not supported")
        except:
            do_log(2,"Unexpected error:" + sys.exc_info()[0])
            raise
    else:
        do_log(1,"Unkown label ("+torrent['label']+"). No Action taken")


