import os

from pyflowlauncher import ResultResponse, Result, send_results, api
from pyflowlauncher.string_matcher import string_matcher, MatchData
from pyflowlauncher.icons import FOLDER

from .anma_data import get_anma_data
from .osettings import osettings, ExtSearch
from .shared import FS_ICO_PATH, PLUGIN_ID, PLUGIN_SETTINGS_DIRECTORY, FAVICON_FOLDER_ROOT, FAVICON_FOLDER_CUSTOM
from .favicon import FaviconManager
from .shiki.types import MediaEntry

import typing as t


class FalseMatchData:
    matched = True
    score = 0


class OSettingsMenu:
    fav_man = FaviconManager([FAVICON_FOLDER_CUSTOM, FAVICON_FOLDER_ROOT])
    
    def __init__(self, lang: t.Literal['ru', 'en'] = 'ru'):
        self.lang = lang
    
    @classmethod
    def external_links(cls, query: str):
        results = list()
        chosen_list = osettings.external_links
        
        for ext_id, ext_name in MediaEntry.EXT_LINKS_NAMES.items():
            if query:
                match = string_matcher(query, ext_name)
            else:
                match = FalseMatchData
            if not match.matched:
                continue
            results.append(
                Result(Title=f"{ext_name} {'[CHOSEN]' if ext_id in chosen_list else ''}",
                       Score=match.score,
                       IcoPath=cls.fav_man.get_fav_path(MediaEntry.EXT_LINKS_HOMEPAGE[ext_id]) or FS_ICO_PATH,
                       ContextData={"type_": "OSettings", "ext_link": ext_id})
            )
        
        return send_results(results=results)
    
    def external_link_context(self, context_data: dict):
        # XXX: Maybe can be simplified with JsonRPC V2 or using shell?
        if context_data['ext_link'] in osettings.external_links:
            osettings.del_external_link(context_data['ext_link'])
            result_str = f"{MediaEntry.EXT_LINKS_NAMES[context_data['ext_link']]} " + "удалён из меню" if self.lang == 'ru' else "deleted from menu"
        else:
            osettings.add_external_link(context_data['ext_link'])
            result_str = f"{MediaEntry.EXT_LINKS_NAMES[context_data['ext_link']]} " + "добавлен в меню" if self.lang == 'ru' else "added to menu"
        osettings.save()
        return send_results(results=[Result(Title=result_str, IcoPath=FS_ICO_PATH)])
    
    @classmethod
    def external_search_delete(cls):
        res = list()
        for exts in osettings.external_search:
            res.append(Result(
                Title=f"{exts.name} ({exts.media_type})",
                SubTitle=exts.url if isinstance(exts.url, str) else f"{exts.url['Anime']}\n{exts.url['Manga']}",
                IcoPath=cls.fav_man.get_fav_path(exts.search("null", 'Anime')) or FS_ICO_PATH,
                ContextData={"type_":"OSettings", "exts_delete": exts.to_dict()}
            ))
        return send_results(results=res)
    
    def external_search_delete_context(self, context_data: dict):
        # XXX: Maybe can be simplified with JsonRPC V2 or using shell?
        ext = ExtSearch(**context_data["exts_delete"])
        osettings.del_external_search(ext)
        osettings.save()
        return send_results(results=[Result(
            Title=f"{ext.name} " + "удалён из меню" if self.lang == 'ru' else "deleted from menu",
            IcoPath=FS_ICO_PATH
        )])
    
    @classmethod
    def external_search_export(cls, query: str):
        res = list()
        data = tuple(map(ExtSearch.from_dict, get_anma_data()))
        for exts in data:
            if query:
                match = string_matcher(query, exts.name)
            else:
                match = FalseMatchData
            if not match.matched:
                continue
            if osettings.check_if_ext_search(exts):
                continue
            res.append(Result(
                Title=f"{exts.name} ({exts.media_type})",
                SubTitle=exts.url if isinstance(exts.url, str) else f"{exts.url['Anime']}\n{exts.url['Manga']}",
                IcoPath=cls.fav_man.get_fav_path(exts.search("null", 'Anime')) or FS_ICO_PATH,
                ContextData={"type_": "OSettings", "exts_add": exts.to_dict()}
            ))
        return send_results(results=res)
    
    def external_search_export_context(self, context_data):
        # XXX: Maybe can be simplified with JsonRPC V2 or using shell?
        exts = ExtSearch(**context_data["exts_add"])
        osettings.add_external_search(exts)
        osettings.save()
        return send_results(results=[Result(
            Title=f"{exts.name} " + "добавлен в меню" if self.lang == 'ru' else "added to menu",
            IcoPath=FS_ICO_PATH
        )])
    
    def external_search_index(self, query: str):
        if query.startswith("d") or query.startswith(":d"):
            return self.external_search_delete()
        if query.startswith("e") or query.startswith(":e"):
            return self.external_search_export(query=query[1:] if query[0] == "e" else query[2:])
        else:
            return send_results(results=[
                Result(
                    Title="s:exts e",
                    SubTitle="Найти сайт из списка" if self.lang == 'ru' else "Add External Search from Available",
                    IcoPath=FS_ICO_PATH
                ),
                Result(
                    Title="s:exts d",
                    SubTitle="Удалить внешний поиск" if self.lang == 'ru' else "Delete External Search",
                    IcoPath=FS_ICO_PATH
                )
            ])
    
    def query(self, query: str):
        if query.startswith("extl"):
            return self.external_links(query[4:].strip())
        elif query.startswith("exts"):
            return self.external_search_index(query[4:].strip())
        else:
            return send_results(results=[
                Result(
                    Title="s:extl",
                    SubTitle="Внешние ссылки" if self.lang == 'ru' else "External Links",
                    IcoPath=FS_ICO_PATH
                ),
                Result(
                    Title="s:exts",
                    SubTitle="Поиск на сайтах" if self.lang == 'ru' else "External Search",
                    IcoPath=FS_ICO_PATH
                ),
                Result(
                    Title="s:rus",
                    SubTitle="Активировать работу с русской раскладкой (ырл)",
                    IcoPath=FS_ICO_PATH,
                    JsonRPCAction=dict(method="Flow.Launcher.AddActionKeyword", parameters=[PLUGIN_ID, "ырл"])
                ),
                # TODO: Fix after v2 implementation in pyflowlauncher
                # Result(
                #     Title="s:folder",
                #     SubTitle="Открыть папку с настройками",
                #     IcoPath=FOLDER,
                #     JsonRPCAction=api.open_directory(PLUGIN_SETTINGS_DIRECTORY, PLUGIN_SETTINGS_DIRECTORY)
                # )
            ])
    
    def context_menu(self, context_data: dict):
        if "ext_link" in context_data:
            return self.external_link_context(context_data)
        elif "exts_delete" in context_data:
            return self.external_search_delete_context(context_data)
        elif "exts_add" in context_data:
            return self.external_search_export_context(context_data)
