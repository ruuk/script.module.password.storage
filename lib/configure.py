import sys, re
import xbmc, xbmcgui
import passwordStorage
from internal import xbmcutil, errors
from internal import getpass as internalGetpass

T = xbmcutil.ADDON.getLocalizedString

class MainWindow(xbmcgui.WindowXML):
	def onInit(self):
		self.infoDisplay = self.getControl(100)
		self.errorsButton = self.getControl(201)
		self.optionsButton = self.getControl(200)
		self.resetButton = self.getControl(202)
		self.updateDisplay()
	
	def onClick(self,controlID):
		if controlID == 200:
			self.keyringOptions()
		elif controlID == 201:
			self.openErrorsWindow()
		elif controlID == 202:
			self.resetKeyring()
			
	def openErrorsWindow(self):
		w = ErrorWindow('password-storage-text.xml' , xbmc.translatePath(xbmcutil.ADDON.getAddonInfo('path')), 'Main',errors=self.errors)
		w.doModal()
		del w
	
	def resetKeyring(self):
		if not xbmcutil.yesNoDialog(T(32035),T(32036),T(32037),T(32035)): return
		
		internalGetpass.clearKeyMemory()
		
		keyring = passwordStorage.getKeyring()
		kr = keyring.get_keyring()
		kr.reset()
		
		passwordStorage.saveKeyToDisk()
		self.updateDisplay()

	def updateDisplay(self):
		keyringName = passwordStorage.getKeyringName()
		text =	'{0}: [COLOR FF66AAFF]{1}[/COLOR][CR][CR]'.format(T(32000),xbmc.getCondVisibility('System.Platform.Android') and 'android' or sys.platform)
		text +=	'{0}: [COLOR FF66AAFF]{1}[/COLOR]'.format(T(32001),keyringName)
		if keyringName.startswith('Internal.'):
			level = securityLevel()
			if level < 0:
				levelText = '[COLOR FF666666]{0}[/COLOR]'.format(T(32005))
			elif level == 0:
				levelText = '[COLOR FFFF0000]{0}[/COLOR]'.format(T(32006))
			elif level == 1:
				levelText = '[COLOR FFFFFF00]{0}[/COLOR]'.format(T(32007))
			elif level == 2:
				levelText = '[COLOR FF0088FF]{0}[/COLOR]'.format(T(32008))
			elif level == 3:
				levelText = '[COLOR FF00FF00]{0}[/COLOR]'.format(T(32009))
				
			text +=	'[CR]{0}: {1}'.format(T(32002),levelText)
			
		text +=	'[CR][CR]{0}: {1}[CR][CR]'.format(
			T(32003),passwordStorage.encrypted and '[COLOR FF00FF00]{0}[/COLOR]'.format(T(32010)) or '[COLOR FFFF0000]{0}[/COLOR]'.format(T(32011))
		)
		
		errors = ''
		if passwordStorage.LAST_ERROR:
			errors = 	'{0}:[CR][CR]'.format(T(32004))
			errors += 	'[COLOR FFFF0000]%s[/COLOR]' % passwordStorage.LAST_ERROR
		self.errors = errors
		self.infoDisplay.setText(text)
		if not bool(self.errors): self.errorsButton.setLabel(T(32032))
		self.errorsButton.setEnabled(bool(self.errors))
		if not keyringName.startswith('Internal'): self.optionsButton.setLabel(T(32033))
		self.optionsButton.setEnabled(keyringName.startswith('Internal'))
		self.resetButton.setEnabled(keyringName.startswith('Internal'))
	
	def keyringOptions(self):
		stored = bool(xbmcutil.ADDON.getSetting('keyring_password'))
		if stored:
			store = T(32012)
		else:
			store = T(32013)
		options = [T(32014),store]
		idx = xbmcgui.Dialog().select(T(32015),options)
		if idx < 0: return
		if idx == 0:
			changeKey()
		elif idx == 1:
			storeKey(not stored)
		self.updateDisplay()
			
class ErrorWindow(xbmcgui.WindowXMLDialog):
	def __init__(self,*args,**kwargs):
		self.errors = kwargs.get('errors','')
	
	def onInit(self):
		self.getControl(100).setText(self.errors)

def changeKey():
	keyring = passwordStorage.getKeyring()
	kr = keyring.get_keyring()
	
	key = internalGetpass.getRememberedKey()
	if key: kr._unlock(key)
	
	if hasattr(kr,'change_keyring_password'):
		internalGetpass.saveRememberedState()
		internalGetpass.clearRememberedKey()
		
		try:
			password = kr.change_keyring_password()
		except errors.AbortException:
			internalGetpass.restoreRememberedState()
			return
		except ValueError:
			internalGetpass.restoreRememberedState()
			xbmcgui.Dialog().ok(T(32016),T(32016))
			return
		except:
			passwordStorage.ERROR('chankeKey(): Unhandled change_keyring_password() error.')
			internalGetpass.restoreRememberedState()
			return

		internalGetpass.saveKeyringPass(password)
		xbmcgui.Dialog().ok(T(32030),T(32031))

def storeKey(store=True,kr=None):
	keyring = passwordStorage.getKeyring()
	kr = kr or keyring.get_keyring()
	if store:
		if hasattr(kr,'change_keyring_password'):
			keyring_key = internalGetpass.getRandomKey()
			try:
				keyring_key = kr.change_keyring_password(keyring_key)
			except ValueError, e:
				xbmcgui.Dialog().ok('Error','Failed to unlock keyring:','',e.message)
				return
			xbmcgui.Window(10000).setProperty('KEYRING_password',keyring_key)
			xbmcutil.ADDON.setSetting('keyring_password',keyring_key)
			xbmcgui.Dialog().ok(T(32017),T(32018))
	else:
		passwordStorage.clearKeyMemory()
		keyring_key = kr.change_keyring_password()
		xbmcutil.ADDON.setSetting('keyring_password','')
		xbmcgui.Window(10000).setProperty('KEYRING_password',keyring_key)
		xbmcgui.Dialog().ok(T(32019),T(32020))
		
def securityLevel():
	if xbmcutil.ADDON.getSetting('keyring_password'): return 0
	password = xbmcgui.Window(10000).getProperty('KEYRING_password')
	if not password: return -1
	level = 1
	if (re.search('\d',password) and re.search('[^\d]',password)) or password.lower() != password or re.search('[\W_]',password): level += 1
	if len(password) > 6: level += 1
	return level

def openWindow():
	w = MainWindow('password-storage-main.xml' , xbmc.translatePath(xbmcutil.ADDON.getAddonInfo('path')), 'Main')
	w.doModal()
	del w
	
if __name__ == '__main__':
	openWindow()
