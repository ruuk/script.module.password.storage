import xbmcgui, hashlib
from internal import xbmcutil

state = None

def getpass(*args,**kwargs):	
	if not kwargs.get('confirm'):
		keyringPass = getRememberedKey()
		if keyringPass: return keyringPass
	if 'confirm' in kwargs: del kwargs['confirm']
	if xbmcutil.ADDON.getSetting('use_remote_control_dialog') == 'true':
		keyringPass = xbmcutil.remoteControlPasswordPrompt(*args,**kwargs)
	else:
		keyringPass = xbmcutil.passwordPrompt(*args,**kwargs)
	return keyringPass

def lazy_getpass(*args,**kwargs):
	keyringPass = getRememberedKey()
	if keyringPass: return keyringPass
	keyringPass = getpass(*args,**kwargs)
	
	if keyringPass: saveKeyringPass(keyringPass)
	
	return keyringPass

def getRememberedKey():
	key =  xbmcgui.Window(10000).getProperty('KEYRING_password') or ''
	#xbmc.getInfoLabel('Window(%s).Property(%s)' % (10000,'KEYRING_password'))
	if not key:
		key = xbmcutil.ADDON.getSetting('keyring_password') or ''
	return key
	
def clearRememberedKey():
	xbmcutil.ADDON.setSetting('keyring_password','')
	clearKeyMemory()

def saveKeyringPass(password):
	xbmcgui.Window(10000).setProperty('KEYRING_password',password)
	#xbmc.executebuiltin('SetProperty(%s,%s,%s)' % ('KEYRING_password',password,10000))

def saveRememberedState():
	global state
	state = (xbmcgui.Window(10000).getProperty('KEYRING_password'),xbmcutil.ADDON.getSetting('keyring_password'))

def restoreRememberedState():
	global state
	if not state: return
	saveKeyringPass(state[0])
	xbmcutil.ADDON.setSetting('keyring_password',state[1] or '')
	
def clearKeyMemory():
	xbmcgui.Window(10000).setProperty('KEYRING_password','')

def getRandomKey():
	import random
	return hashlib.md5(str(random.randint(0,9999999999999999))).hexdigest()

def showMessage(msg):
	xbmcgui.Dialog().ok(xbmcutil.ADDON.getLocalizedString(32023),msg)