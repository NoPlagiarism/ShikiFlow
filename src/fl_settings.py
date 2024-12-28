import logging
import json

from .shared import FL_SETTINGS_FILE

import typing as t

logger = logging.getLogger(__name__)

class FLSettings:
    raw_data: t.Optional[dict] = None
    
    def __init__(self):
        try:
            logger.debug("Loading FL settings file")
            with open(FL_SETTINGS_FILE, mode="r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
        except Exception as e:
            logger.error("Can't read FL settings")
            logger.exception(exc_info=e)
    
    @property
    def language(self) -> t.Optional[str]:
        if self.raw_data is None:
            return None
        return self.raw_data.get("Language")
    
    def get_plugin_settings(self, plugin_id: str) -> t.Optional[dict]:
        if self.raw_data is None:
            return None
        return self.raw_data["PluginSettings"]["Plugins"].get(plugin_id)
    
    def get_plugin_action_keywords(self, plugin_id) -> t.Optional[list[str]]:
        plugin_data = self.get_plugin_settings(plugin_id)
        if plugin_data is None:
            return None
        return plugin_data["ActionKeywords"]
