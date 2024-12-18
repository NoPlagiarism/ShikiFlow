from datetime import datetime
from dataclasses import dataclass
import time
import json
import os

import httpx

from .shared import SECRETS_FILE, APP_NAME, get_version

import logging

import typing as t

logger = logging.getLogger(__name__)


class NoplagiAuthExc(BaseException):
    error: t.Optional[str]
    error_desc: t.Optional[str]
    
    def __init__(self, error: t.Optional[str] = None, error_desc: t.Optional[str] = None):
        self.error, self.error_desc = error, error_desc


@dataclass
class AuthData:
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    created_at: int
    
    @property
    def created_at_dt(self):
        return datetime.fromtimestamp(self.created_at)
    
    @property
    def expire_dt(self):
        return datetime.fromtimestamp(self.created_at + self.expires_in)
    
    @property
    def is_expired(self):
        return int(time.time()) > self.created_at + self.expires_in


class NoplagiAuth(httpx.Auth):
    BASE_URL = httpx.URL("https://shiki.noplagi.xyz/shikiflow/oauth/")
    # BASE_URL = httpx.URL("https://shiki.noplagi.xyz/noplagi-test/oauth/")
    
    authenticated: bool = False
    _auth_data: t.Optional[AuthData] = None
    
    @staticmethod
    def secrets_file_exists() -> bool:
        return os.path.exists(SECRETS_FILE)
    
    @staticmethod
    def check_data(data: t.Union[AuthData, dict]) -> bool:
        if isinstance(data, dict):
            try:
                data = AuthData(**data)
                return True
            except TypeError:
                logger.error(f"Can't read AuthData. Try deleting secrets.json ( {SECRETS_FILE} )")
                return False
    
    @classmethod
    def save_data(cls, data: t.Union[AuthData, dict]):
        if not cls.check_data(data):
            logger.error("Can't save AuthData")
            return
        
        with open(SECRETS_FILE, mode="w+", encoding="utf-8") as f:
            logger.info("Saving secrets")
            json.dump(data, f)
    
    @classmethod
    def delete(cls):
        if cls.secrets_file_exists():
            os.remove(SECRETS_FILE)
    
    def load(self):
        with open(SECRETS_FILE, mode="r", encoding="utf-8") as f:
            data = json.load(f)
        if self.check_data(data):
            self._auth_data = AuthData(**data)
    
    def __init__(self):
        try:
            if self.secrets_file_exists():
                self.load()
        except Exception as e:
            logger.exception("Can't load secrets", exc_info=e)
        self.authenticated = self._auth_data is not None
    
    @classmethod
    def get_start_url(cls, additional_data: t.Dict[str, t.Any]):
        data = {f"{APP_NAME.lower()}_{k}": v for k, v in additional_data.items()}
        return str(cls.BASE_URL.join("start").copy_add_param("additional_data", json.dumps(data)))
    
    "SYNChronous"
    
    def sync_refresh_token(self):
        logger.debug("Refreshing token")
        url = self.BASE_URL.join("refresh")
        raw_resp = httpx.get(url, params=dict(token=self._auth_data.refresh_token))
        resp = raw_resp.json()
        if "error" in resp:
            logger.warning("Got error on refreshing token")
            logger.warning(json.dumps(resp))
            self.authenticated = False
        if self.check_data(resp):
            self.save_data(resp)
            self._auth_data = AuthData(**resp)
            self.authenticated = True
        else:
            logger.warning("Failed to refresh token")
    
    def sync_auth_flow(self, request: httpx.Request) -> t.Generator[httpx.Request, httpx.Response, None]:
        if self.authenticated:
            if self._auth_data.is_expired:
                self.sync_refresh_token()
            if self.authenticated:
                request.headers["Authorization"] = f"{self._auth_data.token_type} {self._auth_data.access_token}"
        response = yield request
        #XXX: could lead to some problems with requests to other user profiles
        if response.status_code == 401 and self.authenticated:
            logger.warning("Got 401, refreshing token & trying again")
            self.sync_refresh_token()
            request.headers["Authorization"] = f"{self._auth_data.token_type} {self._auth_data.access_token}"
            response = yield request
            if response.status_code == 401:
                logger.warning("Got 401 on second try, resetting authentication ")
                self._auth_data = None
                self.authenticated = False
                self.delete()
                request.headers.pop("Authorization")
                yield request
