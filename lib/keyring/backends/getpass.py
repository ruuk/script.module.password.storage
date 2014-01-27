import xbmc, xbmcgui

def getpass(prompt='Enter Password:'):
	keyringPass = getKeyringPass()
	if keyringPass: return keyringPass
	key = xbmc.Keyboard('',prompt,True)
	key.doModal()
	if not key.isConfirmed(): return ''
	keyringPass = key.getText()
	saveKeyringPass(keyringPass)
	return keyringPass

def getKeyringPass():
	password = xbmcgui.Window(10000).getProperty('KEYRING_password') or ''
	if not password:
		import xbmcaddon
		import binascii
		password = binascii.unhexlify(xbmcaddon.Addon('script.module.password.storage').getSetting('keyring_password') or '')
	return password
	
def saveKeyringPass(password):
	xbmcgui.Window(10000).setProperty('KEYRING_password',password)
