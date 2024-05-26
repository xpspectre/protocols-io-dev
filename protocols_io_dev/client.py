import enum
import logging
import requests
from requests.auth import AuthBase

log = logging.getLogger(__name__)


class BearerAuth(AuthBase):
    def __init__(self, token):
        self._token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self._token
        return r


class ProtocolsClientError(Exception):
    pass


class ProtocolFilter(enum.StrEnum):
    public = 'public'
    user_public = 'user_public'
    user_private = 'user_private'
    shared_with_user = 'shared_with_user'


class ProtocolsClient:
    def __init__(self, token: str, base_url: str = 'https://www.protocols.io'):
        self.base_url = base_url  # this is just the scheme+hostname[+port]. Endpoints have different /api/[v3|v4]
        self._auth = BearerAuth(token)
        self._session = requests.Session()
        self._session.auth = self._auth

    def get_profile(self) -> dict:
        res = self._session.get(self.base_url + '/api/v3/session/profile')
        if not res.ok:
            raise ProtocolsClientError(f'Error getting profile: {res.status_code}, {res.text}')
        body = res.json()
        if body.get('status_code') != 0:
            raise ProtocolsClientError(f'Getting profile returned error code {body}')
        return body['user']

    def list_protocols(self, filter: ProtocolFilter, key: str) -> list[dict]:
        params = {'filter': filter, 'key': key}
        return self._get_with_pagination(self.base_url + '/api/v3/protocols', params, 'protocols')

    def get_protocol_steps(self, protocol_id: int) -> list[dict]:
        params = {'content_format': 'json'}
        res = self._session.get(self.base_url + f'/api/v4/protocols/{protocol_id}/steps', params=params)
        if not res.ok:
            raise ProtocolsClientError(f'Error getting protocol {protocol_id} steps: {res.status_code}, {res.text}')
        body = res.json()
        if body.get('status_code') != 0:
            raise ProtocolsClientError(f'Getting protocol {protocol_id} steps returned error code {body}')
        return body['payload']

    def get_protocol_materials(self, protocol_id: int) -> list[dict]:
        res = self._session.get(self.base_url + f'/api/v3/protocols/{protocol_id}/materials')
        if not res.ok:
            raise ProtocolsClientError(f'Error getting protocol {protocol_id} materials: {res.status_code}, {res.text}')
        body = res.json()
        if body.get('status_code') != 0:
            raise ProtocolsClientError(f'Getting protocol {protocol_id} materials returned error code {body}')
        return body['materials']

    def _get_with_pagination(self, url: str, params: dict, data_type: str) -> list[dict]:
        # Get first page
        page_size = 20
        page_params = {**params, 'page_size': page_size}
        res = self._session.get(url, params=page_params)
        if not res.ok:
            raise ProtocolsClientError(f'Error getting {data_type}: {res.status_code}, {res.text}')
        body = res.json()
        # Some of the endpoints return status_code, some don't
        items = body['items']

        # Get the rest of the pages
        # Note it also appears pages are 0-indexed. Items are also 0-indexed. This differs from how API is documented
        #   and how the next_page url works.
        pagination = body['pagination']
        total_pages = pagination['total_pages']
        total_results = pagination['total_results']
        log.info(f'Getting {data_type} has {total_pages} pages, {total_results} items')
        for page_id in range(1, total_pages):
            log.info(f'Getting {data_type} p{page_id + 1}/{total_pages}')
            page_params = {**params, 'page_size': page_size, 'page_id': page_id}
            res = self._session.get(url, params=page_params)
            if not res.ok:
                raise ProtocolsClientError(
                    f'Error getting {data_type} p{page_id + 1}/{total_pages}: {res.status_code}, {res.text}')
            body = res.json()
            items.extend(body['items'])

        assert len(items) == total_results  # interestingly, this pagination API does detect if items change
        return items
