from datetime import date

from enum import Enum

import typing as t

class _SimpleStrEnum(str, Enum):
    def __str__(self):
        return self.value

class MediaEntry:
    id_: int
    mal_id: t.Optional[int] = None
    
    name: t.Optional[str] = None
    russian: t.Optional[str] = None
    license_name_ru: t.Optional[str] = None
    english: t.Optional[str] = None
    japanese: t.Optional[str] = None
    synonyms: t.Optional[tuple[str]] = None
    
    licensors: t.Optional[list[str]] = None
    
    is_censored: t.Optional[bool] = None
    
    url: t.Optional[str] = None
    
    aired_on: t.Optional[date] = None
    description: t.Optional[str] = None
    description_source: t.Optional[str] = None
    
    external_links: t.Optional[dict[str, str]] = None  # kind: url
    
    icon_url: t.Optional[str] = None  # Poster.previewUrl in GraphQL, image in APIv1
    
    type_: str = "none"
    
    def get_names_tuple(self) -> tuple:
        for x in (self.name, self.russian, self.license_name_ru,
                  self.english, self.japanese):
            if x is not None:
                res.append(x)
        if self.synonyms:
            res.extend(self.synonyms)
        
        return tuple(res)
    
    def __repr__(self):
        return f"{self.type_} entry - {self.name} [{self.id_}]"
    
    @property
    def raw_dict(self):
        res = self.__dict__.copy()
        res["type_"] = self.type_
        return res
    
    @classmethod
    def from_raw_dict(cls, raw_dict):
        if raw_dict.get("type_") == "Anime":
            obj = AnimeEntry
        elif raw_dict.get("type_") == "Manga":
            obj = MangaEntry
        else:
            obj = cls
        new = obj()
        new.__dict__.update(raw_dict)
        return new
    
    def get_ext_links_with_names(self) -> t.Optional[dict[str, str]]:
        if self.external_links:
            return dict(tuple(map(lambda k, v: (self.EXT_LINKS_NAMES.get(k, k), v), self.external_links)))
    
    EXT_LINKS_NAMES = {
        "wikipedia": "Wikipedia",
        "myanimelist": "MyAnimeList",
        "anime_db": "AniDB",
        "world_art": "World Art",
        "kinopoisk": "KinoPoisk",
        "kage_project": "Kage Project",
        "twitter": "Twitter/X",
        "smotret_anime": "Anime365",
        "crunchyroll": "Crunchyroll",
        "amazon": "Amazon",
        "hidive": "HIDIVE",
        "hulu": "Hulu",
        "ivi": "IvI",
        "kinopoisk_hd": "KinoPoisk HD",
        "wink": "Wink",
        "netflix": "Netflix",
        "okko": "Okko",
        "youtube": "YouTube",
        "readmanga": "ReadManga",
        "mangalib": "MangaLib",
        "remanga": "ReManga",
        "mangaupdates": "Baka-Updates",
        "mangadex": "MangaDex",
        "mangafox": "MangaFox",
        "mangachan": "MangaChan",
        "mangahub": "MangaHub",
        "novel_tl": "Novel.tl",
        "ruranobe": "RuRanobe",
        "ranobelib": "RanobeLib",
        "novelupdates": "Novel Updates"
    }
    
    EXT_LINKS_HOMEPAGE = {
        "wikipedia": "https://www.wikipedia.org",
        "myanimelist": "https://myanimelist.net",
        "anime_db": "https://anidb.net",
        "world_art": "http://www.world-art.ru/animation",
        "kinopoisk": "https://www.kinopoisk.ru",
        "kage_project": "http://www.world-art.ru/animation",
        "twitter": "https://x.com",
        "smotret_anime": "https://smotret-anime.net",
        "crunchyroll": "https://www.crunchyroll.com",
        "amazon": "https://www.primevideo.com",
        "hidive": "https://www.hidive.com",
        "hulu": "https://www.hulu.com",
        "ivi": "https://www.ivi.ru",
        "kinopoisk_hd": "https://hd.kinopoisk.ru",
        "wink": "https://wink.ru",
        "netflix": "https://www.netflix.com",
        "okko": "https://okko.tv",
        "youtube": "https://youtube.com",
        "readmanga": "https://1.readmanga.io",
        "mangalib": "https://mangalib.me",
        "remanga": "https://remanga.org",
        "mangaupdates": "https://www.mangaupdates.com",
        "mangadex": "https://mangadex.org",
        "mangafox": "https://fanfox.net",
        "mangachan": "https://manga-chan.me",
        "mangahub": "https://mangahub.io",
        "novel_tl": "https://novel.tl",
        "ruranobe": "https://ruranobe.ru",
        "ranobelib": "https://ranobelib.me",
        "novelupdates": "https://www.novelupdates.com"
    }

class AnimeKindEnum(_SimpleStrEnum):
    TV = "tv"
    MOVIE = "movie"
    OVA = "ova"
    ONA = "ona"
    SPECIAL = "special"
    TV_SPECIAL = "tv_special"
    MUSIC = "music"
    PV = "pv"
    CM = "cm"

class AnimeStatusEnum(_SimpleStrEnum):
    ANONS = "anons"
    ONGOING = "ongoing"
    RELEASED = "released"

class AnimeEntry(MediaEntry):
    type_ = "Anime"
    
    kind: t.Optional[AnimeKindEnum] = None
    season: t.Optional[str] = None
    episodes: t.Optional[int] = None
    episodes_aired: t.Optional[int] = None
    status: t.Optional[AnimeStatusEnum] = None

class MangaKindEnum(_SimpleStrEnum):
    MANGA = "manga"
    MANHWA = "manhwa"
    MANHUA = "manhua"
    LIGHT_NOVEL = "light_novel"
    NOVEL = "novel"
    ONE_SHOT = "one_shot"
    DOUJIN = "doujin"

class MangaStatusEnum(_SimpleStrEnum):
    ANONS = "anons"
    ONGOING = "ongoing"
    RELEASED = "released"
    PAUSED = "paused"
    DISCONTINUED = "discontinued"

class MangaEntry(MediaEntry):
    type_ = "Manga"
    
    kind: t.Optional[MangaKindEnum] = None
    status: t.Optional[MangaStatusEnum] = None
    chapters: t.Optional[int] = None
    volumes: t.Optional[int] = None
