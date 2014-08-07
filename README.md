script.module.password.storage
==============================

Kodi (XBMC) module for encrypted password storage via keyring
--------------------------------------
It is currently only available on my [repository](http://ruuks-repo.googlecode.com/files/ruuk.addon.repository-1.0.0.zip).

Support is available at: http://forum.xbmc.org/showthread.php?tid=185631

**Here's some basic usage info:**

'''python
import passwordStorage

username = 'ruuk'
password = 'password'

passwordStorage.store(username,password)
retrieved_password = passwordStorage.retrieve(username)
'''

The default behavior of retrieve() is to ask for the password if none is stored. This can be overridden with ask_on_fail=False:

'''python
retrieved_password = passwordStorage.retrieve(username,ask_on_fail=False)
'''

The ask prompt defaults to "Enter the password for <ADDON_NAME>:" but can be overridden (and generally should) with ask_msg:

'''python
msg = "Enter the password for %s:" % username
retrieved_password = passwordStorage.retrieve(username,ask_msg=msg)
'''

Everything else is handled by the addon. All password storage either uses the platform's encrypted storage or the internal keyring which is also encrypted.
The internal keyring requires unlocking by a passphrase at the first use in an XBMC session. The user can choose to bypass this in the Password Storage options by storing the key to disk. This actually stores a random key to disk so that a users password is never stored unencrypted. While this is still not very secure, the option is there for users who really don't want to be bothered by a request for a password.

There are also some extra functions for encrypting and decrypting data:

'''python
identifier = 'identifying label'
data = 'some test data'
encrypted_data = passwordStorage.encrypt(identifier,data)
decrypted_data = passwordStorage.decrypt(identifier,encrypted_data)
'''

To delete a stored password:

'''python
passwordStorage.delete(username)
'''

To delete an encrypted data key:

'''python
passwordStorage.delete(identifier,for_data=True)
'''


Platforms tested so far:

'''
	Windows XP SP3:         Windows.RegistryKeyring
	ATV2:                   Internal.PythonEncryptedKeyring
	Ouya 1.0.12:            Internal.PythonEncryptedKeyring
	OSX 10.6.3:             OS_X.Keyring
	Ubuntu 13.10/XFCE:      SecretService.Keyring
	OpenELEC 3.0 x86_64:    Internal.PythonEncryptedKeyring
	Android - SG Note 3:    Internal.PythonEncryptedKeyring
	Raspberry Pi (Raspbmc): Internal.PythonEncryptedKeyring
	iOS:                    NOT TESTED
'''
