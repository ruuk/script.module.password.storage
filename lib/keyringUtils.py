import keyring
from keyring import backends, util
from keyring.py27compat import configparser
import xbmc, sys
import getpass

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
				pct=0
				try:
					citems = config.items(section)
					sections[section] = {}
					for name,password in citems:
						name = util.escape.unescape(name)
						sections[section][name] = keyring.get_password(section,name)
						pct+=1
				except configparser.NoSectionError:
					config.remove_section(section)
					LOG('Removing broken section: %s' % section)
					
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
	
	def _get_new_password(self):
		while True:
			password = getpass.getpass("Please set a password for your new keyring: ",force=True)
			confirm = getpass.getpass('Please confirm the password: ',force=True)
			if password != confirm:
				sys.stderr.write("Error: Your passwords didn't match\n")
				continue
			if '' == password.strip():
				# forbid the blank password
				sys.stderr.write("Error: blank passwords aren't allowed.\n")
				continue
			return password
		
		