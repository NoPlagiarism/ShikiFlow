# TODO: support localization

import os
import re
import logging

from pyflowlauncher import Plugin, Result, send_results, api, ResultResponse

from .osettings_menu import OSettingsMenu
from .result import ResultConstructor
from .graphql_queries import GraphQLQueryConstructor
from .search import SearchQLClient
from .shared import FS_ICO_PATH, SETTINGS_TYPE

import typing as t

logger = logging.getLogger(__name__)

plugin = Plugin()

client = SearchQLClient("FlowShiki")
result_constructor = ResultConstructor(settings=plugin.settings)
lang = plugin.settings['language'][:2].lower()
osettings = OSettingsMenu(lang=lang)


class SearchTags:
    TAG_ANIME = "a"
    TAG_MANGA = "m"
    TAG_BOTH = "b"
    TAG_ID = "i"
    TAG_SETTINGS = "s"
    
    original_query: str
    
    tags_found: bool = False
    
    search_only_anime: bool = False
    search_only_manga: bool = False
    search_both_types: bool = False
    
    search_by_id: bool = False
    
    show_settings_menu: bool = False
    
    RAW_TAG_TO_VAR: dict[str, str] = {
        TAG_ANIME: "search_only_anime",
        TAG_MANGA: "search_only_manga",
        TAG_BOTH: "search_both_types",
        TAG_ID: "search_by_id",
        TAG_SETTINGS: "show_settings_menu"
    }
    
    @property
    def clean_query(self):
        if not self.check_colon() and not self.tags_found:
            return self.original_query
        first_colon = self.original_query.find(":")
        return self.original_query[first_colon+1:].strip()
    
    def check_colon(self) -> bool:
        return 0 < self.original_query.find(":") < 3
    
    def get_tags(self) -> t.Optional[str]:
        if self.check_colon():
            return self.original_query[:self.original_query.find(":")].lower()
    
    def __init__(self, query: str):
        self.original_query = query
        
        if (not self.check_colon() and f"{self.TAG_SETTINGS}:" not in query) or "https" in query:
            return
        for tag in self.get_tags():
            if tag not in self.RAW_TAG_TO_VAR:
                continue
            self.__dict__[self.RAW_TAG_TO_VAR[tag]] = True
            self.tags_found = True
        
        # Cleanup
        # Media types
        if ((self.search_only_anime and self.search_only_manga) or  # If am: -> then both
            ((self.search_only_anime or self.search_only_manga) and self.search_both_types) or  # ab,mb = still both
            self.search_by_id):  # Search by ID overrides all media tags
            self.search_only_anime, self.search_only_manga = False, False
            self.search_both_types = True
    
    def get_media_type(self) -> t.Optional[t.Literal['Anime', 'Manga', 'Both']]:
        if self.search_only_anime:
            return 'Anime'
        if self.search_only_manga:
            return 'Manga'
        if self.search_both_types:
            return 'Both'
    
    def get_ids(self) -> tuple[int]:
        return tuple(filter(lambda x: x > 0, tuple(map(int, self.clean_query.split(",")))))


@plugin.on_method
def query(query: str) -> ResultResponse:
    search_tags = SearchTags(query)
    query = search_tags.clean_query
    if search_tags.search_by_id:  # Checking ids beforehand
        try:
            if not search_tags.get_ids():
                raise ValueError("No ids found")
        except Exception as e:
            return send_results([Result(Title="Введите правильные ID" if lang == 'ru' else "Enter valid ids", SubTitle="ReadMe планируется" if lang == 'ru' else "ReadMe is planned", IcoPath=FS_ICO_PATH)], JsonRPCAction=api.open_url("https://github.com/NoPlagiarism/FlowShiki"))
    if search_tags.show_settings_menu:
        return osettings.query(query)
    """ MEDIA ENTRIES """
    if len(query) <= 2:
        return send_results([
            Result(Title="Введите запрос" if lang == 'ru' else "Enter your query", SubTitle="ReadMe планируется" if lang == 'ru' else "ReadMe is planned", IcoPath=FS_ICO_PATH, Score=10, JsonRPCAction=api.open_url("https://github.com/NoPlagiarism/FlowShiki")),
            Result(Title="m:", SubTitle="Искать Мангу" if lang == 'ru' else "Search Manga", IcoPath=FS_ICO_PATH),
            Result(Title="a:", SubTitle="Искать Аниме" if lang == 'ru' else "Search Anime", IcoPath=FS_ICO_PATH),
            Result(Title="b:", SubTitle="Искать Всё" if lang == 'ru' else "Search Both", IcoPath=FS_ICO_PATH)
        ])
    if search_tags.get_media_type() is not None:
        current_search_type = search_tags.get_media_type()
    else:
        current_search_type = plugin.settings.get("default_media_type", "Anime")
    url_matched = re.match(r".*(?P<media_type>animes|mangas)\/(?P<shk_id>\d+).*", query)
    if url_matched:
        media_type_raw = url_matched.group("media_type")
        shk_id = int(url_matched.group("shk_id"))
        data = client.search_by_ids((shk_id, ), media_type_raw[:-1].capitalize())
    elif search_tags.search_by_id:
        data = client.search_both_by_ids(ids=search_tags.get_ids())
    else:
        data = client.search_by_query(query=query, limit=int(plugin.settings.get("limit", "10")), media_type=current_search_type)
    if not data:
        return send_results([Result(
            Title="Нет результатов" if lang == 'ru' else "No results",
            IcoPath=FS_ICO_PATH
        )])
    results = list(result_constructor.result_generator(data))
    if not results:
        return send_results([Result(
            Title="Нет результатов" if lang == 'ru' else "No results",
            IcoPath=FS_ICO_PATH
        )])
    return send_results(results=results)

@plugin.on_method
def context_menu(context_data):
    import json; logger.debug(context_data)
    
    if isinstance(context_data, dict):
        if context_data.get("type_", "") == "OSettings":
            return osettings.context_menu(context_data)
        """ MEDIA ENTRIES """
        if context_data.get("type_", "").lower() in ("anime", "manga"):
            return send_results(result_constructor.make_context_menu(context_data))
