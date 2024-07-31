import logging

from httpx import URL
from pyflowlauncher import Result, api
from pyflowlauncher.icons import BROWSER, COPYLINK, APP

from .shiki.types import MediaEntry, AnimeEntry, MangaEntry,\
    AnimeKindEnum, AnimeStatusEnum, MangaKindEnum, MangaStatusEnum
from .shiki.graphql import MediaEntryFromGraph
from .shared import FS_ICO_PATH, SETTINGS_TYPE, change_query, FAVICON_FOLDER_ROOT, FAVICON_FOLDER_CUSTOM
from .osettings import osettings
from .favicon import FaviconManager

import typing as t

logger = logging.getLogger(__name__)

PREFERABLE_TITLE_TYPE: t.TypeAlias = t.Literal["English", "Russian", "Licensed Russian", "Japanese"]
LANG_TYPE: t.TypeAlias = dict[str, dict[t.T, str]]

class ResultConstructor:
    ANIME_KINDS: LANG_TYPE = {
        "ru": {
            AnimeKindEnum.TV: "TV Сериал",
            AnimeKindEnum.MOVIE: "Фильм",
            AnimeKindEnum.OVA: "OVA",
            AnimeKindEnum.ONA: "ONA",
            AnimeKindEnum.SPECIAL: "Спешл",
            AnimeKindEnum.TV_SPECIAL: "TV Спешл",
            AnimeKindEnum.MUSIC: "Клип",
            AnimeKindEnum.PV: "Проморолик",
            AnimeKindEnum.CM: "Реклама"
        },
        "en": {
            AnimeKindEnum.TV: "TV Series",
            AnimeKindEnum.MOVIE: "Movie",
            AnimeKindEnum.OVA: "OVA",
            AnimeKindEnum.ONA: "ONA",
            AnimeKindEnum.SPECIAL: "Special",
            AnimeKindEnum.TV_SPECIAL: "TV Special",
            AnimeKindEnum.MUSIC: "Music",
            AnimeKindEnum.PV: "PV",
            AnimeKindEnum.CM: "CM"
        }
    }
    ANIME_STATUSES: LANG_TYPE = {
        "ru": {
            AnimeStatusEnum.ANONS: "Анонс",
            AnimeStatusEnum.ONGOING: "Онгоинг",
            AnimeStatusEnum.RELEASED: "Вышло"
        },
        "en": {
            AnimeStatusEnum.ANONS: "Planned",
            AnimeStatusEnum.ONGOING: "Airing",
            AnimeStatusEnum.RELEASED: "Released"
        }
    }
    
    MANGA_KINDS: LANG_TYPE = {
        "ru": {
            MangaKindEnum.MANGA: "Манга",
            MangaKindEnum.MANHWA: "Манхва",
            MangaKindEnum.MANHUA: "Маньхуа",
            MangaKindEnum.LIGHT_NOVEL: "Ранобэ",
            MangaKindEnum.NOVEL: "Новелла",
            MangaKindEnum.ONE_SHOT: "Ваншот",
            MangaKindEnum.DOUJIN: "Додзинси"
        },
        "en": {
            MangaKindEnum.MANGA: "Manga",
            MangaKindEnum.MANHWA: "Manhwa",
            MangaKindEnum.MANHUA: "Manhua",
            MangaKindEnum.LIGHT_NOVEL: "Light Novel",
            MangaKindEnum.NOVEL: "Novel",
            MangaKindEnum.ONE_SHOT: "One Shot",
            MangaKindEnum.DOUJIN: "Doujin"
        }
    }
    MANGA_STATUSES: LANG_TYPE = {
        "ru": {
            MangaStatusEnum.ANONS: "Анонс",
            MangaStatusEnum.ONGOING: "Выходит",
            MangaStatusEnum.RELEASED: "Издано",
            MangaStatusEnum.PAUSED: "Приостановлено",
            MangaStatusEnum.DISCONTINUED: "Прекращено"
        },
        "en": {
            MangaStatusEnum.ANONS: "Planned",
            MangaStatusEnum.ONGOING: "Publishing",
            MangaStatusEnum.RELEASED: "Released",
            MangaStatusEnum.PAUSED: "Paused",
            MangaStatusEnum.DISCONTINUED: "Discontinued"
        }
    }
    
    SEASONS: LANG_TYPE = {
        "ru": {
            "winter": "Зима",
            "spring": "Весна",
            "summer": "Лето",
            "fall": "Осень"
        },
        "en": {
            "winter": "Winter",
            "spring": "Spring",
            "summer": "Summer",
            "fall": "Fall"
        }
    }
    
    def __init__(self, settings: SETTINGS_TYPE, lang: t.Optional[t.Literal['ru', 'en']] = None):
        self.settings = settings
        if lang:
            self.lang = lang
        else:
            self.lang = self.settings.get('language', 'Russian')[:2].lower()
        
        self.fav_man = FaviconManager([FAVICON_FOLDER_CUSTOM, FAVICON_FOLDER_ROOT])

    def result_generator(self, data, preferable_title: PREFERABLE_TITLE_TYPE = "English"):
        for x in (list(data.get("animes", list())) + list(data.get("mangas", list()))):
            yield self.make_result(media=x)
    
    def make_result(self, media: MediaEntry):
        if isinstance(media, AnimeEntry):
            return self.make_result_from_anime(media)
        else:
            return self.make_result_from_manga(media)
    
    @classmethod
    def from_season_string(cls, season: t.Optional[str], lang: t.Literal['ru', 'en']) -> t.Optional[str]:
        if not season:
            return None
        if "_" not in season:
            return None
        return f"{cls.SEASONS[lang][season.split('_')[0]]} {season.split('_')[1]}"
    
    def from_season_string_with_current(self, season: t.Optional[str]) -> t.Optional[str]:
        return self.from_season_string(season, self.lang)
    
    @staticmethod
    def get_preferable_title(media: MediaEntry, preferable_title: PREFERABLE_TITLE_TYPE = "English"):
        if preferable_title == "Licensed Russian" and media.license_name_ru:
            return media.license_name_ru
        if "Russian" in preferable_title and media.russian:
            return media.russian
        if preferable_title == "English":
            return media.english if media.english else media.name
        if preferable_title == "Japanese" and media.japanese:
            return media.japanese
        return media.name
    
    def get_preferable_title_from_chosen(self, media: MediaEntry):
        return self.get_preferable_title(media=media, preferable_title=self.settings['preferable_name'])
    
    @staticmethod
    def find_any_link(media: MediaEntry):
        if not media.is_censored:  # False or None
            return media.url
        # Shiki is censored
        ext_links = media.external_links
        if not ext_links:
            return None
        if "anime_db" in ext_links:
            return ext_links["anime_db"]
        elif "myanimelist" in ext_links:
            return ext_links["myanimelist"]
        return ext_links.values()[0]
    
    def make_result_from_anime(self, anime: AnimeEntry):
        if anime.episodes_aired:
            episodes = str(anime.episodes_aired)
            if anime.episodes_aired < anime.episodes:
                episodes = episodes + "/" + str(anime.episodes)
        else:
            episodes = str(anime.episodes)
        url = self.find_any_link(anime)
        result = Result(
            Title=self.get_preferable_title_from_chosen(anime),
            SubTitle=f"{ {'ru': 'Тип', 'en': 'Format'}[self.lang]}: {self.ANIME_KINDS[self.lang][anime.kind]} | { {'ru': 'Статус', 'en': 'Status'}[self.lang] }: {self.ANIME_STATUSES[self.lang][anime.status]}\n"\
                f"{ {'ru': 'Эпизодов', 'en': 'Episodes'}[self.lang] }: {episodes}" + (f" | { {'ru': 'Сезон', 'en': 'Season' }[self.lang] }: {self.from_season_string_with_current(anime.season)}" if anime.season else ""),
            IcoPath=anime.icon_url,
            ContextData=anime.raw_dict,
            JsonRPCAction=api.open_url(url) if url else api.copy_to_clipboard(self.get_preferable_title_from_chosen(anime))
        )
        return result
    
    def make_result_from_manga(self, manga: MangaEntry):
        ch_vol = "\n"
        if manga.chapters:
            ch_vol = ch_vol + f"{ {'ru': 'Глав', 'en': 'Chapters:' }[self.lang] }: {manga.chapters}"
        if manga.volumes:
            ch_vol = ch_vol + f" | { {'ru': 'Томов', 'en': 'Volumes' }[self.lang] }: {manga.volumes}"
        url = self.find_any_link(manga)
        result = Result(
            Title=self.get_preferable_title_from_chosen(manga),
            SubTitle=f"{ {'ru': 'Тип', 'en': 'Format'}[self.lang]}: {self.MANGA_KINDS[self.lang][manga.kind]} | { {'ru': 'Статус', 'en': 'Status'}[self.lang] }: {self.MANGA_STATUSES[self.lang][manga.status]}" +  ch_vol,
            IcoPath=manga.icon_url,
            ContextData=manga.raw_dict,
            JsonRPCAction=api.open_url(url) if url else api.copy_to_clipboard(self.get_preferable_title_from_chosen(manga))
        )
        return result
    
    def make_context_menu(self, media: MediaEntry | dict):
        if isinstance(media, dict):
            media = MediaEntryFromGraph.from_raw_dict(media)
        
        results = list()
        # URL
        url = self.find_any_link(media)
        if url:
            results.append(Result(
                Title="Скопировать ссылку" if self.lang == 'ru' else "Copy link",
                SubTitle=f"{ {'ru': 'на', 'en': 'on'}[self.lang] } Shikimori" if not media.is_censored else "на {0} (Цензура)".format(str(URL(url).host)),
                IcoPath=COPYLINK,
                JsonRPCAction=api.copy_to_clipboard(url)
            ))
        else:
            results.append(Result(
                Title="URL не найден" if self.lang == 'ru' else "URL not found",
                SubTitle=":<",
                IcoPath=FS_ICO_PATH
            ))
        # ExtLinks
        if media.external_links and osettings.external_links:
            for ext, url_ext in media.external_links.items():
                if ext not in osettings.external_links:
                    continue
                results.append(Result(
                    Title=media.EXT_LINKS_NAMES[ext],
                    SubTitle=f"Открыть на {URL(url_ext).host}" if self.lang == 'ru' else f"Open on {URL(url_ext).host}",
                    IcoPath=self.fav_man.get_fav_path(url_ext) or BROWSER,
                    JsonRPCAction=api.open_url(url_ext)
                ))
        # ExtSearch
        if osettings.external_search:
            for ext in osettings.external_search:
                if ext.media_type != "Both" and ext.media_type != media.type_:
                    continue
                search_url = ext.search(media.name, media.type_.capitalize())
                if not search_url:
                    continue
                logger.debug(search_url)
                results.append(
                    Result(
                        Title=ext.name,
                        SubTitle=f"Искать на {URL(search_url).host}" if self.lang == 'ru' else f"Search on {URL(search_url).host}",
                        IcoPath=self.fav_man.get_fav_path(search_url) or BROWSER,
                        JsonRPCAction=api.open_url(search_url)
                    )
                )
        # names
        """
        results.append(Result(
            Title=media.name,
            SubTitle="Название",
            IcoPath=FS_ICO_PATH,
            JsonRPCAction=api.copy_to_clipboard(media.name)
        ))
        """
        if media.russian:
            results.append(Result(
                Title=media.russian,
                SubTitle="Название на русском" if self.lang == 'ru' else "Russian title",
                IcoPath=FS_ICO_PATH,
                JsonRPCAction=api.copy_to_clipboard(media.russian)
            ))
        if media.english:
            results.append(Result(
                Title=media.english,
                SubTitle="Название на английском" if self.lang == 'ru' else "English title",
                IcoPath=FS_ICO_PATH,
                JsonRPCAction=api.copy_to_clipboard(media.english)
            ))
        if media.synonyms:
            for s in media.synonyms[:3]:
                results.append(Result(
                    Title=s,
                    SubTitle="Альтернативное название" if self.lang == 'ru' else "Alternative title",
                    IcoPath=FS_ICO_PATH,
                    JsonRPCAction=api.copy_to_clipboard(s)
                ))
        if media.license_name_ru:
            licensors = f"({', '.join(media.licensors)})" if media.licensors else ""
            results.append(Result(
                Title=media.license_name_ru,
                SubTitle=f"Лицензированное название {licensors}" if self.lang == 'ru' else f"Ru licensed title {licensors}",
                IcoPath=FS_ICO_PATH,
                JsonRPCAction=api.copy_to_clipboard(media.license_name_ru)
            ))
        if media.japanese:
            results.append(Result(
                Title=media.japanese,
                SubTitle="Название на японском" if self.lang == 'ru' else "Japanese title",
                IcoPath=FS_ICO_PATH,
                JsonRPCAction=api.copy_to_clipboard(media.japanese)
            ))
        
        return results
