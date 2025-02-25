import logging

from .shiki.graphql import GraphQLShikiClient
from .graphql_queries import GraphQLQueryConstructor, GraphQLQueryConstructorWithUserRates
from .shiki.types import AnimeEntry, MangaEntry, MyListString

import typing as t

logger = logging.getLogger(__name__)

class SearchQLClient(GraphQLShikiClient):
    graphql_constructor: GraphQLQueryConstructor
    
    def __init__(self, *args, graphql_constructor: t.Optional[GraphQLQueryConstructor] = None, return_user_rates: t.Optional[bool] = False, **kwargs):
        GraphQLShikiClient.__init__(self, *args, **kwargs)
        if graphql_constructor is not None:
            self.graphql_constructor = graphql_constructor
        else:
            if return_user_rates:
                self.graphql_constructor = GraphQLQueryConstructorWithUserRates()
            else:
                self.graphql_constructor = GraphQLQueryConstructor()
    
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
        data = self.get_data(self.graphql_constructor.anime_get_main_search(search=query, limit=limit))
        return data
    
    def search_manga_by_query(self, query: str, limit: int) -> t.Optional[list[MangaEntry]]:
        data = self.get_data(self.graphql_constructor.manga_get_main_search(search=query, limit=limit))
        return data
    
    def search_both_by_query(self, query: str, limit: int) -> t.Optional[list[AnimeEntry | MangaEntry]]:
        data = self.get_data(self.graphql_constructor.both_get_main_search(search=query, limit=limit))
        return data
    
    def search_anime_by_ids(self, ids: t.Iterable[int]):
        data = self.get_data(self.graphql_constructor.anime_get_main_by_ids(ids))
        return data
    
    def search_manga_by_ids(self, ids: t.Iterable[int]):
        data = self.get_data(self.graphql_constructor.manga_get_main_by_ids(ids))
        return data
    
    def search_both_by_ids(self, ids: t.Iterable[int]):
        data = self.get_data(self.graphql_constructor.both_get_main_by_ids(ids))
        return data
    