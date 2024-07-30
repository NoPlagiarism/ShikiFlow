import asyncio
import base64
from io import BytesIO
import os
import logging

import httpx

import typing as t

logger = logging.getLogger(__name__)

STANDARD_SIZE = 32


class BasicFaviconProvider:    
    @staticmethod
    def simplify_domain(dom: str):
        return dom[4:] if dom.startswith("www.") else dom
    
    @staticmethod
    def get_domain(dom: httpx.URL | str) -> str:
        if isinstance(dom, str):
            if "/" in dom and not (dom.startswith("http://") or dom.startswith("https://")):
                dom = "https://" + dom
            if dom.startswith("https://") or dom.startswith("http://"):
                return httpx.URL(dom).host
            return dom
        return dom.host
    
    # @classmethod
    # def prepare(cls, original_image: Image) -> t.Optional[ImageFile.ImageFile]:
    #     return original_image
    
    # def grab(self, domain: httpx.URL | str) -> t.Optional[ImageFile.ImageFile]:
    #     raise NotImplementedError()
    
    # async def async_grab(self, domain: httpx.URL | str) -> t.Optional[ImageFile.ImageFile]:
    #     raise NotImplementedError()


class JustFromUrlFaviconProvider(BasicFaviconProvider):
    def get_url(self, domain: str | httpx.URL) -> str | httpx.URL:
        raise NotImplementedError()
    
    # def grab(self, domain: httpx.URL | str) -> t.Optional[ImageFile.ImageFile]:
    #     try:
    #         resp = self.client.get(self.get_url(domain))
    #         resp.raise_for_status()
    #         image = Image.open(BytesIO(resp.content))
    #         return self.prepare(image)
    #     except Exception as e:
    #         logger.warning(f"Can't grab favicon from {self.get_domain(domain)}")
    #         logger.exception(e)
    
    # async def async_grab(self, domain: httpx.URL | str) -> t.Optional[ImageFile.ImageFile]:
    #     try:
    #         resp = await self.client.get(self.get_url(domain))
    #         resp.raise_for_status()
    #         image = Image.open(BytesIO(resp.content))
    #         return self.prepare(image)
    #     except Exception as e:
    #         logger.warning(f"Can't grab favicon from {self.get_domain(domain)}")
    #         logger.exception(e)


class GoogleFaviconProvider(JustFromUrlFaviconProvider):
    def get_url(self, domain: str | httpx.URL) -> str:
        return f"https://www.google.com/s2/favicons?sz={STANDARD_SIZE}&domain={self.get_domain(domain)}"

class DDGFaviconProvider(JustFromUrlFaviconProvider):
    def get_url(self, domain: str | httpx.URL) -> str:
        return f"https://icons.duckduckgo.com/ip3/{self.get_domain(domain)}.ico"

class SplitBeeFaviconProvider(JustFromUrlFaviconProvider):
    # empty_img = Image.open(BytesIO(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAxlBMVEUAAABOWZ5CTZhBTZhHUpt7g7d5grZ5gbZ6grZ5grZtd7BtdrBtdq9sdq9sda90fbNzfLNye7Jye7JxerJha6lfaqhfaaheaaddaKdjbatfaqhfaahdZ6eFjLyAh7l/h7l8hLh6grd6grZ3gLVjbapibKpha6lgaqlfaahUX6JTXqFSXaFSXKBRXKD////8/f/x9Pvr7/fm6vXg5fHb4O/V2+vQ1ufJ0eXEzOG/x96+x965wtuzvdiuuNWjrs6dqcuXo8iNmcI0ql5BAAAALnRSTlMACR0dI1BRUVJSiIiIiIi9vby9vdbW1tbW4uLi4uzs7Ozs7Ozx8fHx8f39/f39eytknwAAALdJREFUeJxtz8cWgkAMBVBxsKCIXbH3rqENGoSg/v9PmYGlZpV3F+8khcLvaKLa3J5Ou5YhtCzrtd4sfaW4GJi6ElEffSj2AvDjiSUYjD4SJUkAzjMaGgythUM8Lrh0X3YYduhmGZyQ8MBwlhCHnAGeJK8KfHBjL4NE3hj2yDsi+gAeHlXpnEHVPAA2XYbyAHMgB+2KOswcs0giidPsME1vDNcYvd4r29LzZ0Slc7jcju1SUfvz+xegsB1hwrbzXAAAAABJRU5ErkJggg==")))
    
    def get_url(self, domain: str | httpx.URL) -> str:
        return f"https://favicon.splitbee.io/?url={self.get_domain(domain)}"
    
    # @classmethod
    # def prepare(cls, original_image):
    #     if cls.empty_img.getdata() != original_image.getdata():
    #         return original_image


PROVIDERS = [GoogleFaviconProvider, DDGFaviconProvider, SplitBeeFaviconProvider]


class FaviconManager:
    # client: t.Optional[httpx.Client] = None
    # aclient: t.Optional[httpx.AsyncClient] = None
    
    def __init__(self, cache_paths: list[str]):
        # self.semaphore = asyncio.Semaphore(5)
        
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
    
    # def sync_init_http(self):
    #     self.client = httpx.Client(follow_redirects=True)
    
    # def sync_download_handle(self, domain, _tries=0):
    #     try:
    #         provider = PROVIDERS[_tries](client=self.client)
    #         image = provider.grab(domain)
    #         with open(os.path.join(self.cache_path[-1], BasicFaviconProvider.simplify_domain(provider.get_domain(domain))) + ".png", mode="wb+") as f:
    #             image.save(f)
    #     except Exception as e:
    #         if _tries < len(PROVIDERS)-1:
    #             return self.sync_handle(domain, _tries=_tries+1)
    #         raise e
