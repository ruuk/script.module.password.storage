import appdirs
import xbmc
from internal import xbmcutil

def data_root():
	if xbmc.getCondVisibility('System.Platform.Android'):
		return xbmc.translatePath(xbmcutil.ADDON.getAddonInfo('profile'))
	else:
		return appdirs.user_data_dir('python_keyring','keyring')
