import xbmc, xbmcaddon, sys
from internal import getpass, lazy_getpass, getRememberedKey, xbmcutil, clearKeyMemory, getRandomKey  # analysis:ignore

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

FIRST_RUN = False
if not xbmcaddon.Addon('script.module.password.storage').getSetting('not_first_run_flag'):
	xbmcaddon.Addon('script.module.password.storage').setSetting('not_first_run_flag','true')
	FIRST_RUN = True
	LOG('FIRST RUN')

def saveKeyToDisk():
	kr = keyring.get_keyring()
	if hasattr(kr,'change_keyring_password'):
		keyring_key = getRandomKey()
		keyring_key = kr.change_keyring_password(keyring_key)
		import xbmcgui
		xbmcgui.Window(10000).setProperty('KEYRING_password',keyring_key)
		xbmcaddon.Addon('script.module.password.storage').setSetting('keyring_password',keyring_key)
		
try:
	import keyring
except:
	import internal as keyring
	if FIRST_RUN: saveKeyToDisk()
	
###############################################################################
# Public functions
###############################################################################

def retrieve(username,ask_on_fail=True,ask_msg=None):
	"""
	Get the password associated with the provided username
	If no password is stored or the is an error and ask_on_fail is
	true (default) then shows a dialog asking for the password
	If no password is obtained, returns None
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
		msg = ask_msg or xbmcaddon.Addon('script.module.password.storage').getLocalizedString(32024).format(xbmcaddon.Addon(ADDON_ID).getAddonInfo('name'))
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

def delete(username_or_identifier,for_data=False):
	"""
	Delete the stored password for the associated username from the keyring.
	Seting for_data=True will delete the key for the identifier from a
	previous data encrypt() call.
	"""
	if for_data: username_or_identifier += '_DATA_KEY'
	try:
		keyring.delete_password(SERVICE_NAME,username_or_identifier)
		return True
	except:
		ERROR('Failed to delete password from keyring')
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
	
def encrypt(identifier,data):
	"""
	Encrypt some data. A random key is stored in the keyring for the
	identifier specified, and then used to encrypt the data.
	The returned encrypted data is hex encoded.
	"""
	identifier += '_DATA_KEY' #To avoid collisions with usernames
	from internal.Internal import getRandomKey, encrypt
	key = getRandomKey()
	store(identifier,key)
	return encrypt(key,data)
	
def decrypt(identifier,encrypted_data):
	"""
	Decrypt some previously encrypted data. The key is retrieved from the
	keyring for the	identifier specified, and then used to decrypt the data.
	Returns None if no key is found.
	"""
	identifier += '_DATA_KEY' #To avoid collisions with usernames
	from internal.Internal import decrypt
	key = retrieve(identifier,ask_on_fail=False)
	if not key: return None
	return decrypt(key,encrypted_data)
	
# End Public Functions ########################################################

def __keyringFallback():
	global keyring
	import internal as keyring # analysis:ignore
	if FIRST_RUN: saveKeyToDisk()

encrypted = True
	
try:
	if getKeyringName().startswith('file.'):
		__keyringFallback()
	else:
		keyring.set_password('PasswordStorage_TEST','TEST','test')
		if not keyring.get_password('PasswordStorage_TEST','TEST') == 'test':
			raise Exception()
except:
	ERROR('Keyring failed test - using fallback keyring')
	__keyringFallback()

LOG('Backend: %s' % getKeyringName())
LOG('Platform: %s' % (xbmc.getCondVisibility('System.Platform.Android') and 'android' or sys.platform))
ADDON_ID = None
SERVICE_NAME = None

setAddonID(xbmcaddon.Addon().getAddonInfo('id'))
