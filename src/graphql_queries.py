import typing as t

class GraphQLQueryConstructor:
    media_main_info = "id, malId, name, russian, licenseNameRu, english,"\
            "japanese, synonyms, licensors, isCensored, url, airedOn { date }, externalLinks { kind, url },"\
            "poster { previewUrl, originalUrl }"
    anime_main_info = media_main_info + ", kind, season, episodes, episodesAired, status"
    manga_main_info = media_main_info + ", kind, status, chapters, volumes"
    

    @classmethod
    def anime_get_main_search(cls, search: str, limit: int) -> str:
        query = "query( $search: String = \"%SEARCH%\", $limit: PositiveInt = %LIMIT% )  {"\
            "animes( search: $search, limit: $limit ) { " + cls.anime_main_info + "} }"
        query = query.replace("%SEARCH%", search).replace("%LIMIT%", str(limit))  # XXX: Custom formatter
        return query
    
    @classmethod
    def manga_get_main_search(cls, search: str, limit: int) -> str:
        query = "query( $search: String = \"%SEARCH%\", $limit: PositiveInt = %LIMIT% )  {"\
            "mangas( search: $search, limit: $limit ) { " + cls.manga_main_info + "} }"
        query = query.replace("%SEARCH%", search).replace("%LIMIT%", str(limit))  # XXX: Custom formatter
        return query
    
    @classmethod
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
