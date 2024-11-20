import os
import logging
import json

from pyflowlauncher import Result, ResultResponse
from dataclasses import dataclass

from .shared import OSETTINGS_FILE
from .searchterm import title_search

import typing as t

logger = logging.getLogger(__name__)

@dataclass
class ExtSearch:
    url: str | dict
    name: str
    media_type: t.Literal['Anime', 'Manga', 'Both']
    
    def search(self, title: str, media_type: t.Literal['Anime', 'Manga', 'Both']):
        if isinstance(self.url, str):
            return title_search(self.url, title)
        if media_type not in self.url:
            return
        return title_search(self.url[media_type], title)
    
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class OSettings:
    first_initial: bool = False
    
    def __init__(self, data: t.Optional[dict] = None):
        self._data = data if data else dict()
        self.initialize()
    
    def load(self):
        try:
            with open(OSETTINGS_FILE, mode="r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            logger.info("First init")
            self.first_initial = True
    
    def save(self):
        with open(OSETTINGS_FILE, mode="w+", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=True, indent=4)
    
    def initialize(self):
        self.load()
        
        if "external_links" not in self._data:
            self._data["external_links"] = list()
        if "external_search" not in self._data:
            self._data["external_search"] = list()
        
        if self.first_initial:
            self.save()
    
    @classmethod
    def create_empty(cls):
        return cls()
    
    @property
    def external_links(self) -> list[str]:
        return self._data["external_links"]
    
    def add_external_link(self, kind: str):
        self._data["external_links"].append(kind)
    
    def del_external_link(self, kind: str):
        index = self._data["external_links"].index(kind)
        if index > 0:
            del self._data["external_links"][index]
    
    @property
    def external_search(self):
        return list(map(lambda x: ExtSearch(**x), self._data["external_search"]))
    
    def check_if_ext_search(self, ext: ExtSearch):
        return ext.to_dict() in self._data["external_search"]
    
    def add_external_search(self, ext: ExtSearch):
        ext_data = ext.to_dict()
        if ext_data not in self._data["external_search"]:
            self._data["external_search"].append(ext.to_dict())
    
    def del_external_search(self, ext: ExtSearch):
        index = self._data["external_search"].index(ext.to_dict())
        if index > 0:
            del self._data["external_search"][index]

osettings = OSettings()
