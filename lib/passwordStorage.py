import xbmc, xbmcaddon

import platform, re

original_syscmd_uname = platform._syscmd_uname
def new_syscmd_uname(option,default=''):
	try:
		return platform._syscmd_uname(option,default)
	except:
		return default
platform._syscmd_uname = new_syscmd_uname

import keyring
import getpass # @UnusedImport

## keyring escape fix -----------------------------------
from keyring.util import escape

escape.ESCAPE_FMT = "_%02x"

def unescape(value):
	"""
	Inverse of escape.
	"""
	re_esc = re.compile(
		# the pattern must be bytes to operate on bytes
		escape.ESCAPE_FMT.replace('%02X', '(?P<code>[0-9a-f]{2})').encode('ascii')
	)
	return re_esc.sub(escape._unescape_code, value.encode('ascii')).decode('utf-8')

escape.unescape = unescape
## End keyring escape fix -----------------------------------


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

encrypted = True

def __keyringFallback():
	from internal import PythonEncryptedKeyring
	cryptedKeyring = PythonEncryptedKeyring()  # @UndefinedVariable
	if cryptedKeyring.viable:
		keyring.set_keyring(cryptedKeyring)
	else:
		keyring.set_keyring(keyring.backends.file.PlaintextKeyring)  # @UndefinedVariable
		global encrypted
		LOG('Using un-encrypted keyring')
		encrypted = False
		
# if xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
# 	LOG("OSX or Darwin detected, using fallback keyring")
# 	__keyringFallback()
# else:

def getKeyringName():
	kr = keyring.get_keyring()
	try:
		mod = kr.__module__.rsplit('.',1)[-1]
		cls = kr.__class__.__name__
		return mod + '.' + cls
	except:
		return str(kr).strip('<>').split(' ')[0]
	
try:
	keyring.set_password('PasswordStorage_TEST','TEST','test')
	if not keyring.get_password('PasswordStorage_TEST','TEST') == 'test': raise Exception()
	if getKeyringName() == 'file.EncryptedKeyring':
		from internal import PythonEncryptedKeyring
		keyring.set_keyring(PythonEncryptedKeyring())
		
except:
	ERROR('Keyring failed test - using fallback keyring')
	__keyringFallback()

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

 