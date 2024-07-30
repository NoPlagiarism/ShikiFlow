import logging

from .shiki.graphql import GraphQLShikiClient
from .graphql_queries import GraphQLQueryConstructor
from .shiki.types import AnimeEntry, MangaEntry

import typing as t

logger = logging.getLogger(__name__)

class SearchQLClient(GraphQLShikiClient):
    def search_by_query(self, query: str, limit: int, media_type: t.Literal['Anime', 'Manga', 'Both']) -> t.Optional[list[AnimeEntry | MangaEntry]]:
        if media_type == 'Anime':
            return self.search_anime_by_query(query, limit)
        elif media_type == "Manga":
            return self.search_manga_by_query(query, limit)
        else:
            return self.search_both_by_query(query, limit)
    
    def search_by_ids(self, ids: t.Iterable[int], media_type: t.Literal['Anime', 'Manga', 'Both']) -> t.Optional[list[AnimeEntry | MangaEntry]]:
        if media_type == 'Anime':
            return self.search_anime_by_ids(ids)
        elif media_type == 'Manga':
            return self.search_manga_by_ids(ids)
        else:
            return self.search_both_by_ids(ids)
    
    def search_anime_by_query(self, query: str, limit: int) -> t.Optional[list[AnimeEntry]]:
        data = self.get_data(GraphQLQueryConstructor.anime_get_main_search(search=query, limit=limit))
        return data
    
    def search_manga_by_query(self, query: str, limit: int) -> t.Optional[list[MangaEntry]]:
        data = self.get_data(GraphQLQueryConstructor.manga_get_main_search(search=query, limit=limit))
        return data
    
    def search_both_by_query(self, query: str, limit: int) -> t.Optional[list[AnimeEntry | MangaEntry]]:
        data = self.get_data(GraphQLQueryConstructor.both_get_main_search(search=query, limit=limit))
        return data
    
    def search_anime_by_ids(self, ids: t.Iterable[int]):
        data = self.get_data(GraphQLQueryConstructor.anime_get_main_by_ids(ids))
        return data
    
    def search_manga_by_ids(self, ids: t.Iterable[int]):
        data = self.get_data(GraphQLQueryConstructor.manga_get_main_by_ids(ids))
        return data
    
    def search_both_by_ids(self, ids: t.Iterable[int]):
        data = self.get_data(GraphQLQueryConstructor.both_get_main_by_ids(ids))
        return data
    