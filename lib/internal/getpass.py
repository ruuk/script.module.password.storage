import xbmcgui
import xbmcutil


def getpass(*args,**kwargs):
	import xbmcaddon
	
	if not kwargs.get('confirm'):
		keyringPass = getRememberedKey()
		if keyringPass: return keyringPass
		
	if xbmcaddon.Addon('script.module.password.storage').getSetting('use_remote_control_dialog') == 'true':
		keyringPass = xbmcutil.remoteControlPasswordPrompt(*args,**kwargs)
	else:
		keyringPass = xbmcutil.passwordPrompt(*args,**kwargs)
	return keyringPass

def lazy_getpass(*args,**kwargs):
	keyringPass = getRememberedKey()
	if keyringPass: return keyringPass
	keyringPass = getpass(*args,**kwargs)
	saveKeyringPass(keyringPass)
	return keyringPass

def getRememberedKey():
	key =  xbmcgui.Window(10000).getProperty('KEYRING_password') or ''
	#xbmc.getInfoLabel('Window(%s).Property(%s)' % (10000,'KEYRING_password'))
	if not key:
		import xbmcaddon
		key = xbmcaddon.Addon('script.module.password.storage').getSetting('keyring_password') or ''
	return key
	
def saveKeyringPass(password):
	xbmcgui.Window(10000).setProperty('KEYRING_password',password)
	#xbmc.executebuiltin('SetProperty(%s,%s,%s)' % ('KEYRING_password',password,10000))

def clearKeyMemory():
	xbmcgui.Window(10000).setProperty('KEYRING_password','')
	
def showMessage(msg):
	import xbmcaddon
	xbmcgui.Dialog().ok(xbmcaddon.Addon('script.module.password.storage').getLocalizedString(32023),msg)