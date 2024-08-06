from datetime import date
import json
import logging

from .raw_shiki import BaseShikiClient
from .types import MediaEntry, AnimeEntry, MangaEntry, AnimeKindEnum, AnimeStatusEnum, MangaKindEnum, MangaStatusEnum

import typing as t

logger = logging.getLogger(__name__)


class GraphQLShikiClient(BaseShikiClient):
    def __init__(self, app_name: str):
        # Seems like GraphQL does not need auth for now
        BaseShikiClient.__init__(self, app_name=app_name)
    
    def get_raw_data(self, query: str, variables: t.Optional[dict] = None):
        raw_resp = self.post(f"https://{self.DOMAIN}/api/graphql",
                             data=dict(query=query, variables=variables if variables is not None else dict()))
        raw_resp.raise_for_status()
        resp = raw_resp.json()
        return resp
    
    def get_data(self, query: str, variables: t.Optional[dict] = None):
        data = self.get_raw_data(query=query, variables=variables)
        logger.debug(json.dumps(data, ensure_ascii=False))
        return self.parse_data(data)
    
    @classmethod
    def parse_data(cls, data: dict):
        if "data" in data:
            data = data["data"]
        if "animes" in data:
            data["animes"] = [AnimeEntryFromGraph(x) for x in data["animes"]]
        if "mangas" in data:
            data["mangas"] = [MangaEntryFromGraph(x) for x in data["mangas"]]
        return data


class MediaEntryFromGraph(MediaEntry):
    def __init__(self, data: dict):
        self._data = data
    
    def _try_value(self, name: str | tuple[str], convert: t.Optional[t.Callable] = None,
                   *, custom_data = None):
        data = self._data if custom_data is None else custom_data
        if not isinstance(name, str):
            d = None
            for x in name:
                d = self._try_value(x, convert=convert, custom_data=d)
                if d is None:
                    return
            return d
        if data.get(name):
            if convert and not isinstance(data.get(name), convert):
                return convert(data[name])
            else:
                return data[name]
    
    @property
    def id_(self) -> int:
        return int(self._data['id'])
    
    @property
    def mal_id(self) -> t.Optional[int]:
        return self._try_value("malId", int)
    
    @property
    def name(self) -> t.Optional[str]:
        return self._try_value("name")
    
    @property
    def russian(self) -> t.Optional[str]:
        return self._try_value("russian")
    
    @property
    def license_name_ru(self) -> t.Optional[str]:
        return self._try_value("licenseNameRu")
    
    @property
    def english(self) -> t.Optional[str]:
        return self._try_value("english")
    
    @property
    def japanese(self) -> t.Optional[str]:
        return self._try_value("japanese")
    
    @property
    def synonyms(self) -> t.Optional[tuple[str]]:
        return self._try_value("synonyms", tuple)
    
    @property
    def licensors(self) -> t.Optional[list[str]]:
        return self._try_value("licensors", list)
    
    @property
    def is_censored(self) -> t.Optional[bool]:
        return self._try_value("isCensored")
    
    @property
    def url(self) -> t.Optional[str]:
        if "url" in self._data:
            return self._data["url"]
        return f"https://shikimori.one/{self.type_.lower()}s/{self.id_}"
    
    @property
    def aired_on(self) -> t.Optional[date]:
        return self._try_value(name=("airedOn", "date"), convert=date.fromisocalendar)
    
    @property
    def description(self) -> t.Optional[bool]:
        return self._try_value("description")
    
    @property
    def description_source(self) -> t.Optional[bool]:
        return self._try_value("descriptionSource")
    
    def external_links_builder(self) -> t.Generator[t.Optional[dict[str, str]], None, None]:
        if not self._data.get("externalLinks"):
            return
        for ext in self._data["externalLinks"]:
            yield (ext["kind"], ext["url"])
    
    @property
    def external_links(self) -> t.Optional[dict[str, str]]:
        ext = dict(self.external_links_builder())
        return ext if ext else None
    
    @property
    def icon_url(self) -> t.Optional[str]:
        return self._try_value(("poster", "previewUrl"))
    
    @classmethod
    def from_raw_dict(cls, raw_dict):
        if raw_dict.get("type_") == "Anime":
            obj = AnimeEntryFromGraph
        elif raw_dict.get("type_") == "Manga":
            obj = MangaEntryFromGraph
        else:
            obj = cls
        new = obj(data=raw_dict["_data"])
        return new


class AnimeEntryFromGraph(MediaEntryFromGraph, AnimeEntry):
    @property
    def season(self) -> t.Optional[str]:
        return self._try_value("season")
    
    @property
    def episodes(self) -> t.Optional[int]:
        return self._try_value("episodes", int)
    
    @property
    def episodes_aired(self) -> t.Optional[int]:
        return self._try_value("episodesAired", int)
    
    @property
    def kind(self) -> t.Optional[AnimeKindEnum]:
        return self._try_value("kind", AnimeKindEnum)
    
    @property
    def status(self) -> t.Optional[AnimeStatusEnum]:
        return self._try_value("status", AnimeStatusEnum)

class MangaEntryFromGraph(MediaEntryFromGraph, MangaEntry):
    @property
    def kind(self) -> t.Optional[MangaKindEnum]:
        return self._try_value("kind", MangaKindEnum)
    
    @property
    def status(self) -> t.Optional[MangaStatusEnum]:
        return self._try_value("status", MangaStatusEnum)
    
    @property
    def chapters(self) -> t.Optional[int]:
        return self._try_value("chapters", int)
    
    @property
    def volumes(self) -> t.Optional[int]:
        return self._try_value("volumes", int)
