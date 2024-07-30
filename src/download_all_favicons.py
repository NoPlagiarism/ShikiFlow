# This shit is not working

import os

from .anma_data import get_anma_data
from .shiki.types import MediaEntry
from .favicon import FaviconManager, BasicFaviconProvider

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        @staticmethod
        def write(*args, **kwargs):
            print(*args, **kwargs)
        
        @staticmethod
        def set_description(desc=None, refresh=True):
            if desc is None:
                return
            print(desc)
        
        @staticmethod
        def __call__(iter, *args, **kwargs):
            for x in iter:
                yield x


def get_all_domains():
    anma_data = get_anma_data()
    anma_domains = set([BasicFaviconProvider.simplify_domain(BasicFaviconProvider.get_domain(x['url'] if isinstance(x['url'], str) else x['url']['Anime'])) for x in anma_data])
    extl_domains = set([BasicFaviconProvider.simplify_domain(BasicFaviconProvider.get_domain(x)) for x in MediaEntry.EXT_LINKS_HOMEPAGE.values()])
    domains = anma_domains | extl_domains
    
    fav_man = FaviconManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "Favs"))
    for x in tqdm(domains):
        fav_man.sync_handle(domain=x)


if __name__ == "__main__":
    get_all_domains()
