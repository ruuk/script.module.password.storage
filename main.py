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

def askPassword():
	import keyring
	kr = keyring.get_keyring()
	if getattr(kr,'change_keyring_password',None):
		password = kr.change_keyring_password()
		import binascii
		xbmcaddon.Addon().setSetting('keyring_password',binascii.hexlify(password))
	else:
		xbmcgui.Dialog().ok('Not Required','Keyring does not require','entering a password within XBMC.')
	
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
	if sys.argv[-1] == 'keyring_password':
		askPassword()
	else:
		openWindow()