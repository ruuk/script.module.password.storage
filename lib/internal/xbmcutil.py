import xbmc, xbmcgui, xbmcaddon

ADDON = xbmcaddon.Addon('script.module.password.storage')

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
		self.password = None
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
		
def remoteControlPasswordPrompt(prompt=''):
	w = RemoteControlPassword('password-storage-remote_control_password.xml',xbmc.translatePath(ADDON.getAddonInfo('path')), 'Main',prompt=prompt)
	w.doModal()
	password = w.password
	del w
	return password

def passwordPrompt(prompt=''):
	key = xbmc.Keyboard('',prompt,True)
	key.doModal()
	if not key.isConfirmed(): return None
	password = key.getText()
	return password

def okDialog(heading,msg1,msg2='',msg3=''):
	return xbmcgui.Dialog().ok('',msg1,msg2,msg3)
	
def yesNoDialog(heading,msg1,msg2='',msg3=''):
	return xbmcgui.Dialog().yesno('',msg1,msg2,msg3)