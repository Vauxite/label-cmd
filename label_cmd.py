from deluge_client import DelugeRPCClient
import sys,json,subprocess,os
#Argv
##1 Script_file
##2 Torrent_Id

def readConfig(path):
    with open(path+'') as json_data_file:
        data = json.load(json_data_file)
    return data

config_path = "config/config.json"
secret_path = "config/secrets.json"

config = readConfig(config_path)
secrets = readConfig(secret_path)

Torrent_Id      = "b74fe0edc44974f8635dd6db173931755cf0693d" #= sys.argv[1]


def btw_str(mString, a, b):
    start =  mString.find(a)
    end = mString.find(b, start+1)
    return mString[start+len(a):end]
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
            print "Error unsupported keyValue for torrent: " +key
        print searchword + " : " + replacewith
    
    arg = arg.replace("%%torrentpath%%", torrent['move_completed_path']+'/'+torrent['name'])
    arg = arg.replace("%%torrentname%%", torrent['name'])
    return arg
def do_action(config,torrent):
    action = config['actions'][config['labels'][torrent['label']]['action']]
    executable = action['executable']
    arguments = do_translate(action['arguments'],torrent)
    print  executable+" "+arguments
    
         #result = subprocess.call(executable)
    #result = os.system(executable+" "+arguments
    result ="Success " 
    return result
def get_action(config,torrent):
    action = config['labels'][torrent['label']]['action']
    return config['actions'][action]
if  len(sys.argv) != 1:
    print "Unsupported amount of arguments"
    print "Correct usage: script.py torrent_id"
else:
    client =  DelugeRPCClient(config['deluge']['host'], config['deluge']['port'], secrets['deluge']['user'], secrets['deluge']['passwd'])
    client.connect()
    T_filter = ["label","name","path","move_completed_path"]
    torrent = client.call('core.get_torrent_status', Torrent_Id, T_filter)
    if torrent['label'] in config['labels']:
        try:
            print do_action(config,torrent)
        except WindowsError:
            print "Windows is not supported"
        except subprocess.CalledProcessError:
            print "Attempted action is not supported"
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    else:
        print "Unkown label. No Action taken"
        

   # print torrent


