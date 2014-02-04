import xbmc, xbmcaddon
from internal import getpass, lazy_getpass, getRememberedKey, xbmcutil, clearKeyMemory  # @UnusedImport

import keyring

DEBUG = True
LAST_ERROR = ''

def LOG(msg):
	xbmc.log('script.module.password.storage: ' + msg)
	
def ERROR(msg):
	LOG('ERROR: ' + msg)
	import traceback
	global LAST_ERROR
	LAST_ERROR = traceback.format_exc()
	if not DEBUG:
		return
	traceback.print_exc()

###########################################################################################################
# Public functions
###########################################################################################################

def retrieve(username,ask_on_fail=True,ask_msg=None):
	"""
	Get the password associated with the provided username
	If no password is stored or the is an error and ask_on_fail is true (default) then shows a dialog asking for the password
	If now password is obtained, returns None
	"""
	password = None
	try:
		password = keyring.get_password(SERVICE_NAME,username)
	except ValueError:
		clearKeyMemory()
		password = keyring.get_password(SERVICE_NAME,username)
	except:
		ERROR('Failed to get password from keyring')
	if password:
		return password
	elif ask_on_fail:
		msg = ask_msg or 'Please enter your password for %s:' % xbmcaddon.Addon(ADDON_ID).getAddonInfo('name')
		password = xbmcutil.passwordPrompt(msg)
		if password: return password
	return None

def store(username,password):
	"""
	Save the provided password for the associated username
	Returns true if the password was successfully saved, otherwise false
	"""
	try:
		if not password:
			try:
				keyring.delete_password(SERVICE_NAME,username)
			except:
				pass
		else:
			keyring.set_password(SERVICE_NAME,username,password or '')
			LOG('Password saved via keyring.')
		return True
	except:
		ERROR('Failed to save password to keyring')
	return False

def setAddonID(ID):
	"""
	Set the addon ID for which passwords will be stored
	If this function is not called, it will default use the current addons ID
	"""
	global SERVICE_NAME, ADDON_ID
	ADDON_ID = ID
	SERVICE_NAME = 'PasswordStorage_%s' % ADDON_ID.replace('.','_')
	
def getKeyringName():
	"""
	Returns a somewhat user friendly name of the keyring that is being used
	"""
	kr = keyring.get_keyring()
	try:
		mod = kr.__module__.rsplit('.',1)[-1]
		cls = kr.__class__.__name__
		return mod + '.' + cls
	except:
		return str(kr).strip('<>').split(' ')[0]
	
# End Public Functions ####################################################################################

def __keyringFallback():
	global keyring
	import internal as keyring  # @Reimport @UnusedImport

encrypted = True
	
try:
	if getKeyringName() == 'file.EncryptedKeyring':
		__keyringFallback()
	else:
		keyring.set_password('PasswordStorage_TEST','TEST','test')
		if not keyring.get_password('PasswordStorage_TEST','TEST') == 'test': raise Exception()
except:
	ERROR('Keyring failed test - using fallback keyring')
	__keyringFallback()

LOG('Backend: %s' % getKeyringName())

ADDON_ID = None
SERVICE_NAME = None

setAddonID(xbmcaddon.Addon().getAddonInfo('id'))
