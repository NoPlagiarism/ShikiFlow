import os

from pyflowlauncher import JsonRPCAction

import typing as t

PLUGIN_ID = "b34023f6440d11ef94540242ac120002"

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
FS_ICO_PATH = os.path.join(ROOT_PATH, "Artworks", "logo128.png")

SETTINGS_TYPE = t.TypedDict('Settings', {
	'default_media_type': t.Literal["Anime", "Manga", "Both"],
	'preferable_name': t.Literal["Russian", "Licensed Russian", "English", "Japanese"],
	'limit': str,
	'language': t.Literal['Russian', 'English']
})

FLOW_PROGRAM_DIRECTORY = os.environ.get("FLOW_PROGRAM_DIRECTORY")
FLOW_APPLICATION_DIRECTORY = os.environ.get("FLOW_APPLICATION_DIRECTORY")

def is_portable():
    portable_data_path = os.path.join(FLOW_APPLICATION_DIRECTORY, "UserData")
    portable_data_deletion_indicator = os.path.join(FLOW_APPLICATION_DIRECTORY, "UserData", ".dead")
    return os.path.exists(portable_data_path) and not os.path.exists(portable_data_deletion_indicator)

if is_portable():
    DATA_DIR = os.path.join(FLOW_PROGRAM_DIRECTORY, "UserData")
else:
    DATA_DIR = os.path.expandvars("%APPDATA%\\FlowLauncher")

FL_SETTINGS_FILE = os.path.join(DATA_DIR, "Settings", "Settings.json") if FLOW_PROGRAM_DIRECTORY else None
PLUGIN_SETTINGS_DIRECTORY = os.path.join(DATA_DIR, "Settings", "Plugins", "ShikiFlow") if FLOW_PROGRAM_DIRECTORY else None
SETTINGS_FILE = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "Settings.json") if PLUGIN_SETTINGS_DIRECTORY else None
OSETTINGS_FILE = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "osettings.json") if PLUGIN_SETTINGS_DIRECTORY else None
PLUGIN_CACHE_FOLDER = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "Cache") if PLUGIN_SETTINGS_DIRECTORY else None

FAVICON_FOLDER_ROOT = os.path.join(ROOT_PATH, "Favs")
FAVICON_FOLDER_CUSTOM = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "Favs") if PLUGIN_SETTINGS_DIRECTORY else None
