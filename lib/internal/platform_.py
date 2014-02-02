import appdirs

def data_root():
	return appdirs.user_data_dir('python_keyring','keyring')
