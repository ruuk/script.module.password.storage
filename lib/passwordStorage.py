import xbmc, xbmcaddon

import platform
original_syscmd_uname = platform._syscmd_uname
def new_syscmd_uname(option,default=''):
	try:
		return platform._syscmd_uname(option,default)
	except:
		return default
platform._syscmd_uname = new_syscmd_uname

from keyring.backends import getpass # @UnusedImport
import keyring

DEBUG = True

def LOG(msg):
	xbmc.log('script.module.password.storage: ' + msg)
	
def ERROR(msg):
	LOG('ERROR: ' + msg)
	if not DEBUG: return
	import traceback
	traceback.print_exc()

encrypted = True

def __keyringFallback():
	from keyring import backends
	cryptedKeyring = backends.file.EncryptedKeyring()
	if cryptedKeyring.supported() > -1:
		keyring.set_keyring(cryptedKeyring)
	else:
		keyring.set_keyring(backends.file.PlaintextKeyring)
		global encrypted
		LOG('Using un-encrypted keyring')
		encrypted = False
		
if xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
	LOG("OSX or Darwin detected, using fallback keyring")
	__keyringFallback()
else:
	try:
		keyring.set_password('PasswordStorage_TEST','TEST','test')
		if not keyring.get_password('PasswordStorage_TEST','TEST') == 'test': raise Exception()
	except:
		ERROR('Keyring failed test - using fallback keyring')
		__keyringFallback()
	
def getKeyringName():
	kr = keyring.get_keyring()
	try:
		mod = kr.__module__.rsplit('.',1)[-1]
		cls = kr.__class__.__name__
		return mod + '.' + cls
	except:
		return str(kr).strip('<>').split(' ')[0]

LOG('Backend: %s' % getKeyringName())


def retrieve(username):
	try:
		password = keyring.get_password(SERVICE_NAME,username)
		return password or ''
	except:
		ERROR('Failed to get password from keyring')
	return None

def store(username,password):
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
	global SERVICE_NAME, ADDON_ID
	ADDON_ID = ID
	SERVICE_NAME = 'PasswordStorage_%s' % ADDON_ID.replace('.','_')
	
ADDON_ID = None
SERVICE_NAME = None

setAddonID(xbmcaddon.Addon().getAddonInfo('id'))

 