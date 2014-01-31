import xbmc, xbmcgui

ACTION_MOVE_LEFT      = 1
ACTION_MOVE_RIGHT     = 2
ACTION_MOVE_UP        = 3
ACTION_MOVE_DOWN      = 4
ACTION_SELECT_ITEM    = 7
ACTION_PARENT_DIR     = 9
ACTION_PARENT_DIR2	  = 92
ACTION_PREVIOUS_MENU  = 10

class RemoteControlPassword(xbmcgui.WindowXMLDialog):
	def __init__(self,*args,**kwargs):
		self.password = ''
		self.prompt = kwargs.get('prompt','')
	
	def onInit(self):
		self.getControl(101).setLabel(self.prompt)
		self.passDisplay = self.getControl(100)
		
	def onAction(self,action):
		try:
			if action == ACTION_MOVE_LEFT:
				self.addDigit(4)
			elif action == ACTION_MOVE_RIGHT:
				self.addDigit(6)
			elif action == ACTION_MOVE_UP:
				self.addDigit(8)
			elif action == ACTION_MOVE_DOWN:
				self.addDigit(2)
			elif action == ACTION_SELECT_ITEM:
				self.addDigit(5)
			elif action == ACTION_PARENT_DIR or action == ACTION_PARENT_DIR2:
				self.backspace()
			elif action == ACTION_PREVIOUS_MENU:
				self.close()
		except:
			xbmcgui.WindowXMLDialog.onAction(self,action)
			raise
		
	def updateDisplay(self):
		self.passDisplay.setLabel(len(self.password) * '*')
		
	def addDigit(self,digit):
		if len(self.password) > 7: return
		self.password += str(digit)
		self.updateDisplay()
	
	def backspace(self):
		self.password = self.password[:-1]
		self.updateDisplay()
		
def _getpassRemoteControl(prompt="Enter Remote Sequence:"):
	import xbmcaddon
	w = RemoteControlPassword('password-storage-remote_control_password.xml',xbmc.translatePath(xbmcaddon.Addon('script.module.password.storage').getAddonInfo('path')), 'Main',prompt=prompt)
	w.doModal()
	keyringPass = w.password
	del w
	return keyringPass
	
def _getpass(prompt='Enter Password:'):
	key = xbmc.Keyboard('',prompt,True)
	key.doModal()
	if not key.isConfirmed(): return ''
	keyringPass = key.getText()
	return keyringPass

def getpass(*args,**kwargs):
	import xbmcaddon
	if xbmcaddon.Addon('script.module.password.storage').getSetting('use_remote_control_dialog') == 'true':
		keyringPass = _getpassRemoteControl(*args,**kwargs)
	else:
		keyringPass = _getpass(*args,**kwargs)
	return keyringPass

def lazy_getpass(*args,**kwargs):
	keyringPass = getKeyringPass()
	if keyringPass: return keyringPass
	keyringPass = getpass(*args,**kwargs)
	saveKeyringPass(keyringPass)
	return keyringPass

def getRememberedKey():
	return xbmcgui.Window(10000).getProperty('KEYRING_password') or ''
	#xbmc.getInfoLabel('Window(%s).Property(%s)' % (10000,'KEYRING_password'))
	
def getKeyringPass():
	password = getRememberedKey()
	
	if not password:
		import xbmcaddon
		import binascii
		password = binascii.unhexlify(xbmcaddon.Addon('script.module.password.storage').getSetting('keyring_password') or '')
	return password
	
def saveKeyringPass(password):
	xbmcgui.Window(10000).setProperty('KEYRING_password',password)
	#xbmc.executebuiltin('SetProperty(%s,%s,%s)' % ('KEYRING_password',password,10000))
