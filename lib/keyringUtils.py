import keyring
from keyring import backends, util
from keyring.py27compat import configparser
import xbmc

def LOG(msg):
	xbmc.log('script.module.password.storage: ' + msg)
	
class EnhancedEncryptedKeyring(backends.file.EncryptedKeyring):
	def change_keyring_password(self,new_password):
		LOG('EnhancedEncryptedKeyring: change_password() - START')
		config = configparser.RawConfigParser()
		config.read(self.file_path)
		sections = {}
		for section in config.sections():
			section = util.escape.unescape(section)
			if section != 'keyring-setting':
				sections[section] = {}
				pct=0
				for name,password in config.items(section):
					name = util.escape.unescape(name)
					sections[section][name] = keyring.get_password(section,name)
					pct+=1
				LOG('Loaded section: %s (%s passwords)')
		self._init_file()
		LOG('Changed keyring password')
		for section, items in section.items():
			for name, password in items.items():
				keyring.set_password(section,name,password)
			LOG('Saved section %s' % section)
		LOG('EnhancedEncryptedKeyring: change_password() - END')
		
		