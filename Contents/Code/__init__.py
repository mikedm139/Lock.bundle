import os

PREFIX = "/applications/lock"

NAME = 'Lock'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
LOCK_ICON = 'Lock.png'
UNLOCK_ICON = 'Unlock.png'


def Start():
	HTTP.CacheTime = 0
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)

@handler(PREFIX, NAME, "icon-default.png", "art-default.jpg")
def MainMenu():
			Dict['unlockpass'] = LoadData(Prefs['unlockpass'])
			basePathLock = '/Users/<YOURUSERNAME>/Desktop/Lock.command'
			basePathUnlock = '/Users/<YOURUSERNAME>/Desktop/Unlock.command'
			oc = ObjectContainer(no_cache=True)
			oc.add(DirectoryObject(key=Callback(LaunchApplication, path = basePathLock), title="Lock", thumb=R(LOCK_ICON)))	
			if Prefs['unlock'] and Dict['unlockpass'] == '<CHOOSEAPASSWORD>':
				oc.add(DirectoryObject(key=Callback(LaunchApplication, path = basePathUnlock), title="Unlock", thumb=R(UNLOCK_ICON)))
			return oc

@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	Dict['unlockpass'] = LoadData(Prefs['unlockpass'])
	if Prefs['unlock'] and Dict['unlockpass']=='<CHOOSEAPASSWORD>':
		#Prefs['unlock'] = True
		MainMenu()


@route(PREFIX + '/load')
def LoadData(value):
    unlockpass = value
    return unlockpass


def LaunchApplication(path):
	os.system("open " + path)
	return MessageContainer(header = 'Lock', message = 'Application Successfully Launched')