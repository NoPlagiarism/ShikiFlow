from functools import cache
import os
import json

from pyflowlauncher import JsonRPCAction

import typing as t

PLUGIN_ID = "b34023f6440d11ef94540242ac120002"

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
PLUGIN_JSON = os.path.join(ROOT_PATH, "plugin.json")
FS_ICO_PATH = os.path.join(ROOT_PATH, "Artworks", "logo128.png")

SETTINGS_TYPE = t.TypedDict('Settings', {
	'default_media_type': t.Literal["Anime", "Manga", "Both"],
	'preferable_name': t.Literal["Russian", "Licensed Russian", "English", "Japanese"],
	'limit': str,
	'language': t.Literal['Russian', 'English']
})

FLOW_PROGRAM_DIRECTORY = os.environ.get("FLOW_PROGRAM_DIRECTORY")
FL_SETTINGS_FILE = os.path.join(FLOW_PROGRAM_DIRECTORY, "UserData", "Settings", "Settings.json") if FLOW_PROGRAM_DIRECTORY else None
PLUGIN_SETTINGS_DIRECTORY = os.path.join(FLOW_PROGRAM_DIRECTORY, "UserData", "Settings", "Plugins", "ShikiFlow") if FLOW_PROGRAM_DIRECTORY else None
SETTINGS_FILE = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "Settings.json") if PLUGIN_SETTINGS_DIRECTORY else None
OSETTINGS_FILE = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "osettings.json") if PLUGIN_SETTINGS_DIRECTORY else None
PLUGIN_CACHE_FOLDER = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "Cache") if PLUGIN_SETTINGS_DIRECTORY else None
SECRETS_FILE = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "secrets")

FAVICON_FOLDER_ROOT = os.path.join(ROOT_PATH, "Favs")
FAVICON_FOLDER_CUSTOM = os.path.join(PLUGIN_SETTINGS_DIRECTORY, "Favs") if PLUGIN_SETTINGS_DIRECTORY else None

APP_NAME = "ShikiFlow"

@cache
def get_version():
	with open(PLUGIN_JSON, encoding="utf-8", mode="r") as f:
		plugin = json.load(f)
	return plugin["Version"]
