import keyring
from keyring import backends, util
from keyring.py27compat import configparser
import xbmc

def LOG(msg):
	xbmc.log('script.module.password.storage: ' + msg)
	
class EnhancedEncryptedKeyring(backends.file.EncryptedKeyring):
	def change_keyring_password(self):
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
				LOG('Loaded section: %s (%s passwords)' % (section,pct))
		self._init_file()
		LOG('Changed keyring password')
		removes = []
		for section, items in sections.items():
			for name, password in items.items():
				if password:
					keyring.set_password(section,name,password)
				else:
					removes.append((section,name))
			LOG('Saved section %s' % section)
		if removes:
			config = configparser.RawConfigParser()
			config.read(self.file_path)
			for section,name in removes:
				config.remove_option(section, name)
			with open(self.file_path, 'w') as config_file:
				config.write(config_file)
			LOG('Removed %s broken entries' % len(removes))
		
		LOG('EnhancedEncryptedKeyring: change_password() - END')
		return self.keyring_key
		
		