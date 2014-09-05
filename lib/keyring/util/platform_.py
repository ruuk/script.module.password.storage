# from __future__ import absolute_import
# 
# import os
# import platform
# 
# def _data_root_Windows():
# 	try:
# 		root = os.environ['LOCALAPPDATA']
# 	except KeyError:
# 		# Windows XP
# 		root = os.path.join(os.environ['USERPROFILE'], 'Local Settings')
# 	return os.path.join(root, 'Python Keyring')
# 
# def _data_root_Linux():
# 	"""
# 	Use freedesktop.org Base Dir Specfication to determine storage
# 	location.
# 	"""
# 	fallback = os.path.expanduser('~/.local/share')
# 	root = os.environ.get('XDG_DATA_HOME', None) or fallback
# 	return os.path.join(root, 'python_keyring')
# 
# # by default, use Unix convention
# data_root = globals().get('_data_root_' + platform.system(), _data_root_Linux)
import appdirs
import os, sys

def data_root():
    return appdirs.user_data_dir('python_keyring','keyring')

_config_root_Windows = data_root

def _config_root_Linux():
    """
    Use freedesktop.org Base Dir Specfication to determine config
    location.
    """
    fallback = os.path.expanduser('~/.local/share')
    key = 'XDG_DATA_HOME' # TODO: use XDG_CONFIG_HOME, ref #99.
    root = os.environ.get(key, None) or fallback
    return os.path.join(root, 'python_keyring')

if sys.platform.startswith('win'):
    config_root = _config_root_Windows
else:
    config_root = _config_root_Linux
