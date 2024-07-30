from datetime import datetime

import httpx

import typing as t
import logging

class BaseShikiClass:
    DOMAIN = "shikimori.one"


class ShikimoriAuthorizationCode(httpx.Auth):
    FORCE_APP_NAME: bool = True
    
    def __init__(self, client_id: str, client_secret: str,
                 app_name: str,
                 access_token: t.Optional[str] = None, refresh_token: t.Optional[str] = None,
                 redirect_uri: t.Optional[str] = None):
        self.client_id, self.client_secret = client_id, client_secret
        self.app_name = app_name
        self.redirect_uri = redirect_uri if redirect_uri is not None else "urn:ietf:wg:oauth:2.0:oob"
        self.access_token = access_token
        self.refresh_token = refresh_token
        
        self.expires: t.Optional[datetime] = None
    
    def auth_flow(self, request: httpx.Request) -> t.Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = "Bearer " + self.access_token
        if self.FORCE_APP_NAME and self.app_name:
            request.headers["User-Agent"] = self.app_name
        
        if self.expires:
            if self.expires < datetime.now():
                self.refresh_access_token()
        
        resp = yield request
        if resp.status_code == 401:
            self.refresh_access_token()
            yield request
    
    def get_auth_grant_url(self, scope: t.Optional[t.Union[str, tuple, list]] = None) -> httpx.URL:
        if not isinstance(scope, str):
            scope = ",".join(scope)
        elif not scope:
            scope = ""
        
        return httpx.URL(f"https://{self.DOMAIN}/oauth/authorize").copy_merge_params(dict(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            response_type="code",
            scope=scope
        ))
    
    def get_new_access_token(self, auth_code: str):
        with httpx.Client(headers={"User-Agent": self.app_name}) as client:  # XXX: move getting client to separate function
            raw_resp = client.post(f"https://{self.DOMAIN}/oauth/token",
                               data=dict(
                                   grant_type="authorization_code",
                                   client_id=self.client_id,
                                   client_secret=self.client_secret,
                                   code=auth_code,
                                   redirect_uri=self.redirect_uri
                               ))
            raw_resp.raise_for_status()  # XXX: Error handling?
            resp = raw_resp.json()
        
        self.access_token = resp["access_token"]
        self.refresh_token = resp["refresh_token"]
        self.expires = datetime.utcfromtimestamp(resp["created_at"] + resp["expires_in"])
    
    def refresh_access_token(self):
        with httpx.Client(headers={"User-Agent": self.app_name}) as client:
            raw_resp = client.post(f"https://{self.DOMAIN}/oauth/token",
                                   data=dict(
                                       grant_type="refresh_token",
                                       client_id=self.client_id,
                                       client_secret=self.client_secret,
                                       refresh_token="REFRESH_TOKEN"
                                   ))
            raw_resp.raise_for_status()
            resp = raw_resp.json()
        
        self.access_token = resp["access_token"]
        self.refresh_token = resp["refresh_token"]
        self.expires = datetime.utcfromtimestamp(resp["created_at"] + resp["expires_in"])


class BaseShikiClient(BaseShikiClass, httpx.Client):
    _auth: t.Optional[ShikimoriAuthorizationCode]
    
    def __init__(self, app_name: str,
                 *,
                 client_id: t.Optional[str] = None, client_secret: t.Optional[str] = None,
                 access_token: t.Optional[str] = None, refresh_token: t.Optional[str] = None,
                 redirect_uri: t.Optional[str] = None):
        self.app_name = app_name
        
        if client_id is not None and client_secret is not None:
            auth = ShikimoriAuthorizationCode(client_id=client_id, client_secret=client_secret,
                                              app_name=app_name,
                                              access_token=access_token, refresh_token=refresh_token,
                                              redirect_uri=redirect_uri)
        else:
            auth = None
        
        httpx.Client.__init__(self, auth=auth, headers={"User-Agent": self.app_name})

    @property
    def auth(self) -> t.Optional[ShikimoriAuthorizationCode]:
        return self._auth
    
    def get_auth_grant_url(scope: t.Optional[t.Union[str, tuple, list]] = None) -> t.Optional[httpx.URL]:
        if self._auth:
            return self._auth.get_auth_grant_url(scope)
