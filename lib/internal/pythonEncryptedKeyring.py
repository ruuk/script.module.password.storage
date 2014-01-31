import aes, pyDes, hashlib, os, binascii
try:
	from lib import keyring  # @UnusedImport
except:
	#For testing
	import keyring  # @UnusedImport @Reimport
	
from keyring.backends.file import BaseKeyring, json
from keyring.util import properties
from keyring.errors import PasswordDeleteError
try:
	from lib import getpass  # @UnusedImport
	from lib.getpass import lazy_getpass
except:
	#For testing
	import getpass  #@Reimport
	lazy_getpass = getpass.getpass

def LOG(msg):
	print 'script.module.password.storage: ' + msg
	
class PythonEncryptedKeyring(BaseKeyring):
	_check = 'password reference value'
	
	filename = 'python_crypted_pass.json'
	
	@properties.ClassProperty
	@classmethod
	def priority(self):
		return .6
	
	@properties.NonDataProperty
	def keyring_key(self):
		# _unlock or _init_file will set the key or raise an exception
		if self._check_file():
			self._unlock()
		else:
			self._init_file()
		return self.keyring_key

	def _init_file(self):
		"""
		Initialize a new password file and set the reference password.
		"""
		import random
		self.keyring_key = self._get_new_password()
		#We create and encrypt and store a secondary key, so the primary key can be changed and all we need to do is decrypt and restore the secondary
		secondary_key = hashlib.md5(str(random.randint(0,9999999999999999))).hexdigest()
		passwords_dict = {	'key':self.encrypt(self.keyring_key, secondary_key),
							'check':self.encrypt(self.keyring_key, self._check)
		}
		self._write_passwords(passwords_dict)
	
	def _check_file(self):
		"""
		Check if the file exists and has the expected password reference.
		"""
		if not os.path.exists(self.file_path): return False
		passwords_dict = self._read_passwords()
		return 'check' in passwords_dict
	
	def _check_reference(self,passwords_dict):
		try:
			check = self.decrypt(self.keyring_key, passwords_dict['check'])
			assert check == self._check
		except (ValueError,AssertionError):
			self._lock()
			return False
		return True
	
	def _unlock(self):
		"""
		Unlock this keyring by getting the password for the keyring from the
		user.
		"""
		self.keyring_key = lazy_getpass('Please enter password for encrypted keyring: ')
		print "TEST"
		passwords_dict = self._read_passwords()
		if not self._check_reference(passwords_dict): raise ValueError("Incorrect Password")

	def _lock(self):
		"""
		Remove the keyring key from this instance.
		"""
		del self.keyring_key
		
	def _get_secondary_key(self,passwords_dict):
		return self.decrypt(self.keyring_key, passwords_dict['key'])
		
	def change_keyring_password(self):
		passwords_dict = self._read_passwords()
		key = self._get_secondary_key(passwords_dict)
		self.keyring_key = self._get_new_password()
		passwords_dict['key'] = self.encrypt(self.keyring_key, key)
		passwords_dict['check'] = self.encrypt(self.keyring_key, self._check)
		self._write_passwords(passwords_dict)
		
	def get_password(self, service, username):
		"""
		Read the password from the file.
		"""
		passwords_dict = self._read_passwords()
		key = self._get_secondary_key(passwords_dict)
		try:
			return self.decrypt(key, passwords_dict[service][username])
		except KeyError:
			return None
		

	def set_password(self, service, username, password):
		"""Write the password in the file.
		"""
		passwords_dict = self._read_passwords()
		key = self._get_secondary_key(passwords_dict)
		if not service in passwords_dict: passwords_dict[service] = {}
		encrypted_password = self.encrypt(key, password)
		passwords_dict[service][username] = encrypted_password
		self._write_passwords(passwords_dict)
		

	def delete_password(self, service, username):
		"""Delete the password for the username of the service.
		"""
		passwords_dict = self._read_passwords()
		try:
			del passwords_dict[service][username]
		except KeyError:
			raise PasswordDeleteError("Password not found")
		self._write_passwords(passwords_dict)
			
	def _get_new_password(self):
		while True:
			password = getpass.getpass("Please set a password for your new keyring: ")
			confirm = getpass.getpass('Please confirm the password: ')
			if password != confirm:
				LOG("Error: Your passwords didn't match\n")
				continue
			if '' == password.strip():
				# forbid the blank password
				LOG("Error: blank passwords aren't allowed.\n")
				continue
			return password
		
	def _read_passwords(self):
		if not os.path.exists(self.file_path): self._init_file()
		with open(self.file_path,'r') as pass_file:
			return json.load(pass_file)
		
	
	def _write_passwords(self,passwords_dict):
		with open(self.file_path,'w') as pass_file:
			json.dump(passwords_dict,pass_file,separators=(',',':'),sort_keys=True,indent=4)
	
	def encrypt(self, key, password):
		password = self._encryptDes(key,password)
		return binascii.hexlify(aes.encryptData(hashlib.md5(key).digest(),password))

	def decrypt(self, key, password_encrypted):
		password = aes.decryptData(hashlib.md5(key).digest(),binascii.unhexlify(password_encrypted))
		return self._decryptDes(key,password)

	def _encryptDes(self,key,password):
		des = pyDes.triple_des(hashlib.md5(key).digest())
		return des.encrypt(password,padmode=pyDes.PAD_PKCS5)
		
	def _decryptDes(self,key,password):
		des = pyDes.triple_des(hashlib.md5(key).digest())
		return des.decrypt(password,padmode=pyDes.PAD_PKCS5)
