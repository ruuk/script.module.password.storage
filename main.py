import sys
import xbmc, xbmcgui, xbmcaddon

class MainWindow(xbmcgui.WindowXML):
	def __init__(self,*args,**kwargs):
		self.text = kwargs.get('text','')
		self.errors = kwargs.get('errors','')
	
	def onInit(self):
		self.getControl(100).setText(self.text)
		self.getControl(101).setText(self.errors)
	
	def onClick(self,controlID):
		if controlID == 200:
			xbmcaddon.Addon().openSettings()

def changePassword():
	from passwordStorage import keyring# @UnresolvedImport
	kr = keyring.get_keyring()
	if hasattr(kr,'change_keyring_password'):
		xbmcgui.Window(10000).setProperty('KEYRING_password','')
		xbmcaddon.Addon('script.module.password.storage').setSetting('keyring_password','')
		
		password = kr.change_keyring_password()
		import binascii
		xbmcaddon.Addon().setSetting('keyring_password',binascii.hexlify(password))
		xbmcgui.Window(10000).setProperty('KEYRING_password',password)
	else:
		xbmcgui.Dialog().ok('Not Required','Keyring does not require','entering a password within XBMC.')
	
def storeKey(store=True):
	addon = xbmcaddon.Addon()
	if store:
		from passwordStorage import keyring# @UnresolvedImport
		kr = keyring.get_keyring()
		if hasattr(kr,'change_keyring_password'):
			addon.setSetting('keyring_password',kr.keyring_key)
	else:
		addon.setSetting('keyring_password','')
		
def openWindow():
	import passwordStorage  # @UnresolvedImport
	text =	'Keyring: [COLOR FF66AAFF]%s[/COLOR][CR][CR]' % passwordStorage.getKeyringName()
	text +=	'Uses Encrypted Storage: %s[CR][CR]' % (passwordStorage.encrypted and '[COLOR FF00FF00]Yes[/COLOR]' or '[COLOR FFFF0000]No[/COLOR]')
	errors = ''
	if passwordStorage.LAST_ERROR:
		errors = 	'ERRORS:[CR][CR]'
		errors += 	'[COLOR FFFF0000]%s[/COLOR]' % passwordStorage.LAST_ERROR
	w = MainWindow('password-storage-main.xml' , xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')), 'Main',text=text,errors=errors)
	w.doModal()
	del w
	
if __name__ == '__main__':
	if sys.argv[-1] == 'store_key':
		storeKey()
	elif sys.argv[-1] == 'clear_key':
		storeKey(False)
	else:
		openWindow()