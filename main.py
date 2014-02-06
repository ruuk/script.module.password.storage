import sys, re
import xbmc, xbmcgui, xbmcaddon

class MainWindow(xbmcgui.WindowXML):
	def onInit(self):
		self.updateDisplay()
	
	def onClick(self,controlID):
		if controlID == 200:
			xbmcaddon.Addon().openSettings()
			self.updateDisplay()
		elif controlID == 201:
			self.openErrorsWindow()
			
	def openErrorsWindow(self):
		w = ErrorWindow('password-storage-text.xml' , xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')), 'Main',errors=self.errors)
		w.doModal()
		del w
	
	def updateDisplay(self):
		import passwordStorage  # @UnresolvedImport
		keyringName = passwordStorage.getKeyringName()
		text =	'Platform: [COLOR FF66AAFF]%s[/COLOR][CR][CR]' % (xbmc.getCondVisibility('System.Platform.Android') and 'android' or sys.platform)
		text +=	'Keyring: [COLOR FF66AAFF]%s[/COLOR]' % keyringName
		if keyringName.startswith('Internal.'):
			level = securityLevel()
			if level < 0:
				levelText = '[COLOR FF666666]UNKNOWN[/COLOR]'
			elif level == 0:
				levelText = '[COLOR FFFF0000]POOR[/COLOR]'
			elif level == 1:
				levelText = '[COLOR FFFFFF00]LOW[/COLOR]'
			elif level == 2:
				levelText = '[COLOR FF0088FF]MEDIUM[/COLOR]'
			elif level == 3:
				levelText = '[COLOR FF00FF00]HIGH[/COLOR]'
				
			text +=	'[CR]Security Level: %s' % levelText
			
		text +=	'[CR][CR]Uses Encrypted Storage: %s[CR][CR]' % (passwordStorage.encrypted and '[COLOR FF00FF00]Yes[/COLOR]' or '[COLOR FFFF0000]No[/COLOR]')
		
		errors = ''
		if passwordStorage.LAST_ERROR:
			errors = 	'ERRORS:[CR][CR]'
			errors += 	'[COLOR FFFF0000]%s[/COLOR]' % passwordStorage.LAST_ERROR
		self.errors = errors
		self.getControl(100).setText(text)
		self.getControl(201).setEnabled(bool(self.errors))
			
class ErrorWindow(xbmcgui.WindowXMLDialog):
	def __init__(self,*args,**kwargs):
		self.errors = kwargs.get('errors','')
	
	def onInit(self):
		self.getControl(100).setText(self.errors)

def changePassword():
	from passwordStorage import keyring# @UnresolvedImport
	kr = keyring.get_keyring()
	if hasattr(kr,'change_keyring_password'):
		xbmcaddon.Addon('script.module.password.storage').setSetting('keyring_password','')
		password = ''
		while not password:
			xbmcgui.Window(10000).setProperty('KEYRING_password','')
			try:
				password = kr.change_keyring_password()
			except ValueError:
				xbmcgui.Dialog().ok('Incorrect Password','Wrong password.')
				continue
		stored = xbmcaddon.Addon().getSetting('keyring_password')
		if stored:
			import binascii
			xbmcaddon.Addon().setSetting('keyring_password',binascii.hexlify(password))
		xbmcgui.Window(10000).setProperty('KEYRING_password',password)
	else:
		xbmcgui.Dialog().ok('Not Required','The current keyring does not require','entering a password within XBMC.')
	
def storeKey(store=True):
	addon = xbmcaddon.Addon()
	from passwordStorage import keyring, clearKeyMemory# @UnresolvedImport
	kr = keyring.get_keyring()
	if store:
		if hasattr(kr,'change_keyring_password'):
			from lib.internal import getRandomKey
			keyring_key = getRandomKey()
			keyring_key = kr.change_keyring_password(keyring_key)
			xbmcgui.Window(10000).setProperty('KEYRING_password',keyring_key)
			addon.setSetting('keyring_password',keyring_key)
			xbmcgui.Dialog().ok('Stored','Keyring password is now stored on disk.')
	else:
		clearKeyMemory()
		keyring_key = kr.change_keyring_password()
		addon.setSetting('keyring_password','')
		xbmcgui.Window(10000).setProperty('KEYRING_password',keyring_key)
		xbmcgui.Dialog().ok('Removed','Keyring password is no longer stored on disk.')
		
def securityLevel():
	if xbmcaddon.Addon().getSetting('keyring_password'): return 0
	password = xbmcgui.Window(10000).getProperty('KEYRING_password')
	if not password: return -1
	level = 1
	if (re.search('\d',password) and re.search('[^\d]',password)) or password.lower() != password or re.search('[\W_]',password): level += 1
	if len(password) > 6: level += 1
	return level

def openWindow():
	w = MainWindow('password-storage-main.xml' , xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')), 'Main')
	w.doModal()
	del w
	
if __name__ == '__main__':
	if sys.argv[-1] == 'store_key':
		storeKey()
	elif sys.argv[-1] == 'clear_key':
		storeKey(False)
	elif sys.argv[-1] == 'change_key':
		changePassword()
	else:
		openWindow()