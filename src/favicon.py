import asyncio
import base64
from io import BytesIO
import os
import logging

import httpx

import typing as t

logger = logging.getLogger(__name__)

# 2nd level domains where subdomains used
GLOBAL_DOMAINS = [
    "wikipedia.org",
    "slashlib.me",
    "readmanga.io",
    "yaoilib.net"
]


class BasicFaviconProvider:    
    @staticmethod
    def simplify_domain(dom: str):
        res = dom[4:] if dom.startswith("www.") else dom
        for x in GLOBAL_DOMAINS:
            if dom.endswith(x):
                return x
        return res
    
    @staticmethod
    def get_domain(dom: httpx.URL | str) -> str:
        if isinstance(dom, str):
            if "/" in dom and not (dom.startswith("http://") or dom.startswith("https://")):
                dom = "https://" + dom
            if dom.startswith("https://") or dom.startswith("http://"):
                return httpx.URL(dom).host
            return dom
        return dom.host


class FaviconManager:    
    def __init__(self, cache_paths: list[str]):
        
        self.cache_paths = [x for x in cache_paths if x]  # Escape None's in arguments
        
        for path in self.cache_paths:
            if not os.path.exists(path):
                os.makedirs(path)
    
    @staticmethod
    def get_fav_path_in_folder(dom: str | httpx.URL, path: str) -> t.Optional[str]:
        fav_path = os.path.join(path, BasicFaviconProvider.simplify_domain(BasicFaviconProvider.get_domain(dom)) + ".png")
        if os.path.exists(fav_path):
            return fav_path
    
    def get_fav_path(self, dom: str | httpx.URL) -> t.Optional[str]:
        for path in self.cache_paths:
            fav_path = self.get_fav_path_in_folder(dom, path)
            if fav_path:
                return fav_path
