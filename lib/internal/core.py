"""
core.py

Created by Kang Zhang on 2009-07-09
"""
_keyring_backend = None

def set_keyring(keyring):
    """Set current keyring backend.
    """
    global _keyring_backend
    _keyring_backend = keyring


def get_keyring():
    """Get current keyring backend.
    """
    return _keyring_backend


def get_password(service_name, username):
    """Get password from the specified service.
    """
    return _keyring_backend.get_password(service_name, username)


def set_password(service_name, username, password):
    """Set password for the user in the specified service.
    """
    _keyring_backend.set_password(service_name, username, password)


def delete_password(service_name, username):
    """Delete the password for the user in the specified service.
    """
    _keyring_backend.delete_password(service_name, username)


def init_backend():
    """
    Load a keyring specified in the config file or infer the best available.
    """
    from pythonEncryptedKeyring import PythonEncryptedKeyring
    set_keyring(PythonEncryptedKeyring())



init_backend()
