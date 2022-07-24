import os.path

PROJECT_NAME = 'Newer Super Mario Bros. DS Patch Wizard'
FULL_PROJECT_NAME = 'Newer Super Mario Bros. DS Patch Wizard'
PROJECT_VERSION = '1.03'

WIN_ICON = os.path.join('data', 'icon.ico')
MAC_ICON = None
MAC_BUNDLE_IDENTIFIER = None

SCRIPT_FILE = 'patch_wizard.py'
DATA_FOLDERS = ['data']
DATA_FILES = ['readme.txt', 'license.txt']
EXTRA_IMPORT_PATHS = []

USE_PYQT = True
USE_NSMBLIB = False

EXCLUDE_SELECT = True
EXCLUDE_HASHLIB = False
EXCLUDE_LOCALE = True

# macOS only
AUTO_APP_BUNDLE_NAME = SCRIPT_FILE.split('.')[0] + '.app'
FINAL_APP_BUNDLE_NAME = FULL_PROJECT_NAME + '.app'
