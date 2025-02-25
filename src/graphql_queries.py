from enum import Enum

from .shiki.types import MyListString
import typing as t

class GraphQLQueryConstructor:
    media_main_info = "id, malId, name, russian, licenseNameRu, english,"\
            "japanese, synonyms, licensors, isCensored, url, airedOn { date }, externalLinks { kind, url },"\
            "poster { previewUrl, originalUrl }"
    _anime_info_to_add = ", kind, season, episodes, episodesAired, status"
    anime_main_info = media_main_info + _anime_info_to_add
    _manga_info_to_add = ", kind, status, chapters, volumes"
    manga_main_info = media_main_info + _manga_info_to_add
    

    @staticmethod
    def _mylist_decor(func):
        def wrapper(*args, mylist: t.Optional[t.Union[MyListString, list[MyListString], str, list[MyListString]]] = None, **kwargs):
            query: str = func(*args, **kwargs)
            
            if mylist is None:
                return query
            elif isinstance(mylist, list):
                mylist = ",".join(mylist)
            
            # injecting
            SUPPORTED_QUERIES = ("animes", "mangas")
            for x in SUPPORTED_QUERIES:
                query.replace(f"{x}(", f"{x}( mylist: {mylist}, ")
            
            return query
        return wrapper

    @classmethod
    @_mylist_decor
    def anime_get_main_search(cls, search: str, limit: int) -> str:
        query = "query( $search: String = \"%SEARCH%\", $limit: PositiveInt = %LIMIT% )  {"\
            "animes( search: $search, limit: $limit ) { " + cls.anime_main_info + "} }"
        query = query.replace("%SEARCH%", search).replace("%LIMIT%", str(limit))  # XXX: Custom formatter
        return query
    
    @classmethod
    @_mylist_decor
    def manga_get_main_search(cls, search: str, limit: int) -> str:
        query = "query( $search: String = \"%SEARCH%\", $limit: PositiveInt = %LIMIT% )  {"\
            "mangas( search: $search, limit: $limit ) { " + cls.manga_main_info + "} }"
        query = query.replace("%SEARCH%", search).replace("%LIMIT%", str(limit))  # XXX: Custom formatter
        return query
    
    @classmethod
    @_mylist_decor
    def both_get_main_search(cls, search: str, limit: int) -> str:
        if limit % 2:
            limit += 1
        query = "query( $search: String = \"%SEARCH%\", $limit: PositiveInt = %LIMIT% )  {"\
                "animes( search: $search, limit: $limit ) { " + cls.anime_main_info + "} "\
                "mangas( search: $search, limit: $limit ) { " + cls.manga_main_info + "} }"
        query = query.replace("%SEARCH%", search).replace("%LIMIT%", str(limit // 2))
        return query
    
    @staticmethod
    def _get_string_ids(ids: t.Iterable[int]) -> str:
        ids_string = ",".join(tuple(map(str, ids)))
        return ids_string
    
    @classmethod
    def anime_get_main_by_ids(cls, ids: t.Iterable[int]) -> str:
        query = "query( $ids: String = \"%IDS%\", $limit: PositiveInt = %LIMIT% ) {"\
            "animes ( ids: $ids, limit: $limit ) {" + cls.anime_main_info + "} }"
        query = query.replace("%IDS%", cls._get_string_ids(ids)).replace("%LIMIT%", str(len(ids)+1))
        return query
    
    @classmethod
    def manga_get_main_by_ids(cls, ids: t.Iterable[int]) -> str:
        query = "query( $ids: String = \"%IDS%\", $limit: PositiveInt = %LIMIT% ) {"\
            "mangas ( ids: $ids, limit: $limit ) {" + cls.manga_main_info + "} }"
        query = query.replace("%IDS%", cls._get_string_ids(ids)).replace("%LIMIT%", str(len(ids)+1))
        return query
    
    @classmethod
    def both_get_main_by_ids(cls, ids: t.Iterable[int]) -> str:
        query = "query( $ids: String = \"%IDS%\", $limit: PositiveInt = %LIMIT% ) {"\
                "animes ( ids: $ids, limit: $limit ) {" + cls.anime_main_info + "} "\
                "mangas ( ids: $ids, limit: $limit ) {" + cls.manga_main_info + "} }"
        query = query.replace("%IDS%", cls._get_string_ids(ids)).replace("%LIMIT%", str(len(ids)+1))
        return query


class GraphQLQueryConstructorWithUserRates(GraphQLQueryConstructor):
    user_rate = "userRate { id, volumes, chapters, episodes, rewatches, score, status }"
    media_main_info = GraphQLQueryConstructor.media_main_info + ", " + user_rate
    anime_main_info = media_main_info + GraphQLQueryConstructor._anime_info_to_add
    manga_main_info = media_main_info + GraphQLQueryConstructor._manga_info_to_add
