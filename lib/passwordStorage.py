import xbmc, xbmcaddon, sys
from internal import xbmcutil, errors
from internal import getpass as internalGetpass

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
if not xbmcutil.ADDON.getSetting('not_first_run_flag'):
	xbmcutil.ADDON.setSetting('not_first_run_flag','true')
	FIRST_RUN = True
	LOG('FIRST RUN')
		
keyring = None

def __keyringFallback():
	import internal as keyring # analysis:ignore
	if FIRST_RUN: saveKeyToDisk()
	return keyring

encrypted = True

def getKeyring(): #Use this so we only get the keyring when needed. This avoids unnecessary keyring password prompts when the user enters the incorrect password.
	global keyring
	if keyring: return keyring
	try:
		import keyring
	except errors.AbortException:
		LOG('Keyring import - User aborted keyring unlock!!!')
	except:
		ERROR('Error importing keyring')
		keyring = __keyringFallback()
		LOG('Backend: %s' % getKeyringName(keyring))
		return keyring
	
	try:
		if getKeyringName().startswith('file.'):
			keyring = __keyringFallback() #analysis:ignore
		else:
			keyring.set_password('PasswordStorage_TEST','TEST','test')
			if not keyring.get_password('PasswordStorage_TEST','TEST') == 'test':
				raise Exception()
	except errors.AbortException:
		LOG('At test - User aborted keyring unlock!!!')
	except errors.IncorrectKeyringKeyException:
		LOG('User entered bad keyring key')
	except:
		ERROR('Keyring failed test - using fallback keyring')
		keyring = __keyringFallback()

	LOG('Backend: %s' % getKeyringName(keyring))
	return keyring

def saveKeyToDisk():
	keyring = getKeyring()
	kr = keyring.get_keyring()
	if hasattr(kr,'change_keyring_password'):
		keyring_key = internalGetpass.getRandomKey()
		kr._init_file(keyring_key)
		keyring_key = kr.change_keyring_password(keyring_key)
		
		internalGetpass.saveKeyringPass(keyring_key)
		xbmcutil.ADDON.setSetting('keyring_password',keyring_key)

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
	keyring = getKeyring()
	password = None
	try:
		password = keyring.get_password(SERVICE_NAME,username)
	except errors.AbortException:
		LOG('retreive() 1 - User aborted keyring unlock!!!')
		xbmcutil.okDialog('Failed','Keyring remains locked.','','Could not get the Facebook password from the keyring.')
	except errors.IncorrectKeyringKeyException:
		LOG('retreive() 1 - User entered incorrect keyring password!!!')	
		xbmcutil.okDialog('Failed','Incorrect keyring password.','','Could not get the Facebook password from the keyring.')
	except ValueError:
		try:
			internalGetpass.clearKeyMemory()
			password = keyring.get_password(SERVICE_NAME,username)
		except errors.AbortException:
			LOG('retreive() 2 - User aborted keyring unlock!!!')	
			xbmcutil.okDialog('Failed','Keyring remains locked.','','Could not get the Facebook password from the keyring.')
		except errors.IncorrectKeyringKeyException:
			LOG('retreive() 2 - User entered incorrect keyring password!!!')	
			xbmcutil.okDialog('Failed','Incorrect keyring password.','','Could not get the Facebook password from the keyring.')
		except:
			ERROR('Failed to get password from keyring')
	except:
		ERROR('Failed to get password from keyring')
		
	if password: return password
		
	if ask_on_fail:
		msg = ask_msg or xbmcutil.ADDON.getLocalizedString(32024).format('[B]{0}[/B]'.format(xbmcaddon.Addon(ADDON_ID).getAddonInfo('name')))
		password = xbmcutil.passwordPrompt(msg)
		if password: return password

		xbmcutil.okDialog('Failed','Failed to retreive password.')

	return None

def store(username,password,only_if_unlocked=False):
	"""
	Save the provided password for the associated username
	Returns true if the password was successfully saved, otherwise false
	"""
	if only_if_unlocked:
		if getKeyringName().startswith('Internal.'):
			if not internalGetpass.getRememberedKey(): return
	keyring = getKeyring()
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
	Setting for_data=True will delete the key for the identifier from a
	previous data encrypt() call.
	"""
	keyring = getKeyring()
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
	If this function is not called, it will default use the current addon's ID
	"""
	global SERVICE_NAME, ADDON_ID
	ADDON_ID = ID
	SERVICE_NAME = 'PasswordStorage_%s' % ADDON_ID.replace('.','_')
	
def getKeyringName(keyring=None):
	"""
	Returns a somewhat user friendly name of the keyring that is being used
	"""
	keyring = keyring or getKeyring()
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
	from internal.Internal import encrypt
	key = internalGetpass.getRandomKey()
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

LOG('Platform: %s' % (xbmc.getCondVisibility('System.Platform.Android') and 'android' or sys.platform))
ADDON_ID = None
SERVICE_NAME = None

setAddonID(xbmcaddon.Addon().getAddonInfo('id'))
