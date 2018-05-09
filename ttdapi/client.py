import requests
from urllib.parse import urljoin
import logging

from ttdapi.exceptions import TTDApiPermissionsError, TTDApiError

logger = logging.getLogger(__name__)


class BaseTTDClient(requests.Session):
    """
    The TDD Client can
    - authenticate with username/password and get a token.
    -  cache existing tokens and seamlessly get new ones
    -  perform authenticated requests
    - [TODO] implements retry policy on 500
    - reuses underlying TCP connection for better performance


    The authentication headers are automatically used for each request,
    they are updated whenever a access_token is set


    Do not use this client for any nonthetradedesk urls otherwise your
    token will be exposed

    """

    def __init__(self, login, password,
                 token_expires_in=90,
                 base_url="https://api.thetradedesk.com/v3/"):
        super().__init__()
        self.base_url = base_url
        self._login = login
        self._password = password
        self.token_expires_in = token_expires_in

        self._token = None

    def _build_url(self, endpoint):
        return urljoin(self.base_url, endpoint.lstrip("/"))

    @property
    def token(self):
        """Get or reuse token"""
        if self._token is None:
            self._refresh_token(self.token_expires_in)
        return self._token

    @token.setter
    def token(self, new_token):
        """Set access token + update auth headers"""
        logger.debug("Setting new access token")
        self._token = new_token

        logger.debug("Updating TTD-Auth header")
        self.headers.update({"TTD-Auth": new_token})

    def _refresh_token(self, expires_in=90):

        logger.debug("Getting new access token")
        data = {
            "Login": self._login,
            "Password": self._password,
            "TokenExpirationInMinutes": expires_in
        }

        resp = self.request("POST", self._build_url('authentication'), json=data)
        try:
            resp.raise_for_status()
        except requests.HTTPError as err:
            if err.response.status_code in (401, 403):
                raise TTDApiPermissionsError("{}\n{}".format(err, err.response.text))
            else:
                raise TTDApiError(err.response.text)

        self.token = resp.json()["Token"]

    def _request(self, method, url, *args, **kwargs):
        """Do authenticated HTTP request

        Implements retry on expired access token

        Returns:
            requests.Response object
        """

        # auth headers are set when requesting token
        resp = self.request(method, url, *args, **kwargs)
        try:
            resp.raise_for_status()
        except requests.HTTPError as err:
            if err.response.status_code == 403:
                # token expired
                logger.debug("Token expired or invalid, trying again")
                self._refresh_token()
                try:
                    resp2 = self.request(method, url, *args, **kwargs)
                    resp2.raise_for_status()
                except requests.HTTPError as err:
                    raise TTDApiError("{}\n{}".format(err, err.response.text))
                else:
                    return resp2
            else:
                raise TTDApiError("{}\n{}".format(err, err.response.text))
        else:
            return resp

    def get(self, endpoint, *args, **kwargs):
        """Make an authenticated get request against the API endpoint

        Args:
            standard requests.get() parameters

        Returns:
            json response
        """
        return self._request("GET", self._build_url(endpoint), *args, **kwargs).json()


    def post(self, endpoint, *args, **kwargs):
        """Make an authenticated POST request against the API endpoint

        Args:
            standard requests.post() parameters

        Returns:
            json response
        """
        return self._request("POST", self._build_url(endpoint), *args, **kwargs).json()

    def put(self, endpoint, *args, **kwargs):
        """Make an authenticated POST request against the API endpoint

        Args:
            standard requests.put() parameters

        Returns:
            json response
        """

        return self._request("PUT", self._build_url(endpoint), *args, **kwargs).json()



class TTDClient(BaseTTDClient):
    """
    Contains shortcut methods for some endpoints (create_campaign, etc...)

    """
    def create_campaign(self, data):
        return self.post('/campaign', json=data)

    def create_adgroup(self, data):
        return self.post('/adgroup')

    def update_adgroup(self, data):
        return self.post('/adgroup')

    def update_campaign(self, data):
        return self.put('/campaign', json=data)

    def get_sitelist(self, id_):
        return self.get('/sitelist/{}'.format(id_))
