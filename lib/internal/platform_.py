import appdirs
import xbmc

def data_root():
	if xbmc.getCondVisibility('System.Platform.Android'):
		import xbmcaddon
		return xbmc.translatePath(xbmcaddon.Addon('script.module.password.storage').getAddonInfo('profile'))
	else:
		return appdirs.user_data_dir('python_keyring','keyring')
