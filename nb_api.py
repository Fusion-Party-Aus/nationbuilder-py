# nb_api.py ---
#
# Filename: nb_api.py
# Description: Base functionality for the NationBuilder API
# Author: Niklas Rehfeld
# Copyright 2014 Niklas Rehfeld
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#

"""
Base functionality for the NationBuilder APIs.

Classes:
    NationBuilderAPI
     -- Base class of the other APIs.
    NBResponseError(Exception)
     -- Base Exception for non-200 server responses
    NBNotFoundError(NBResponseError)
     -- Exception signifying that the object (person/tag/etc.) that was queried
       was not found. Usually in response to a 404 response from the server.
    NBBadRequestError(NBResponseError)
     -- Exception signifying that the data sent to the server was bad. Usually
        in response to a 400 response from the server.

Basic Usage:

To find all people tagged with the tag "foo":

nb = NationBuilderApi("mynation", "FFAA55DDFFAA22")
tags = nb.tags().get_people_by_tag("foo")
print tags

"""

import logging
import os
from typing import Optional

import requests
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

API_TOKEN = os.getenv("NATIONBUILDER_API_TOKEN")
SITE_SLUG = os.getenv("NATIONBUILDER_SITE_SLUG", "fusion")  # futureparty is the Science Party

log = logging.getLogger('nbpy')


class NationBuilderApi(object):
    # https://nationbuilder.com/api_documentation

    def __init__(self, nation_slug, api_key):
        """
        Create a NationBuilder Connection. All of the base URLs need to be here rather than the child classes since
        they reference each other a bit.

        Parameters:
            slug : the nation slug (e.g. foo in foo.nationbuilder.com)
            token : the access token or test token from nationbuilder
        """
        self.NATION_SLUG = nation_slug
        self.ACCESS_TOKEN = api_key
        self.BASE_URL = ''.join(['https://', self.NATION_SLUG,
                                 '.nationbuilder.com/api/v1'])
        self.PAGINATE_QUERY = "?page={page}&per_page={per_page}"

        # https://nationbuilder.com/blogs_api
        self.BLOGS_URL = self.BASE_URL + '/sites/{0}/pages/blogs'
        self.BLOG_POSTS_URL = self.BLOGS_URL + '{1}/posts'

        # List API URLs
        self.LIST_INDEX_URL = self.BASE_URL + '/lists' + self.PAGINATE_QUERY
        self.GET_LIST_URL = ''.join((self.BASE_URL, '/lists/{list_id}/people',
                                     self.PAGINATE_QUERY))
        # https://nationbuilder.com/basic_pages_api
        self.PAGES_URL = self.BASE_URL + '/sites/{0}/pages/basic_pages'
        # People API URLs.
        self.GET_PEOPLE_URL = self.BASE_URL + '/people'
        self.GET_PERSON_URL = self.GET_PEOPLE_URL + '/{0}'
        self.MATCH_PERSON_URL = self.BASE_URL + '/people/match?'
        self.MATCH_EMAIL_URL = self.BASE_URL + "/people/match?email={0}"
        self.SEARCH_PERSON_URL = (self.GET_PEOPLE_URL + '/search'
                                  + self.PAGINATE_QUERY)
        self.NEARBY_URL = (self.GET_PEOPLE_URL + '/nearby'
                           + self.PAGINATE_QUERY + '&location={lat},{lng}'
                           + '&distance={dist}')
        self.UPDATE_PERSON_URL = self.GET_PERSON_URL
        self.REGISTER_PERSON_URL = self.GET_PERSON_URL + "/register"

        # Contacts API URLs
        self.GET_CONTACT_URL = self.GET_PERSON_URL + "/contacts"
        self.CONTACT_TYPES_URL = self.BASE_URL + '/settings/contact_types'
        self.UPDATE_CONTACT_TYPE_URL = self.CONTACT_TYPES_URL + '/{id}'
        self.CONTACT_METHODS_URL = self.BASE_URL + '/settings/contact_methods'
        self.CONTACT_STATUS_URL = self.BASE_URL + '/settings/contact_statuses'
        # https://nationbuilder.com/sites_api
        self.SITES_URL = self.BASE_URL + '/sites'
        # Tags API URLs
        self.PERSON_TAGS_URL = self.GET_PERSON_URL + "/taggings"
        self.REMOVE_TAG_URL = self.PERSON_TAGS_URL + "/{1}"
        self.LIST_TAGS_URL = self.BASE_URL + "/tags" + self.PAGINATE_QUERY
        self.GET_BY_TAG_URL = ''.join((self.BASE_URL, "/tags/{tag}/people",
                                       self.PAGINATE_QUERY))

        self.USER_AGENT = "nbpy/0.2"

        self.HEADERS = {
            'Content-type': 'application/json',
            "Accept": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        self.session: Optional[AuthorizedSession] = None

    def get_response_from_authenticated_call(self, url: str, params: dict) -> dict:
        response = self.session.get(url, headers=self.HEADERS, params=params)
        self._check_response(response=response, attempted_action=None, url=url)
        return response.json()

    def _check_response(self, response: requests.Response, attempted_action: Optional[str], url=None):
        """Log a warning if this is not a 200 OK response,
        otherwise log the response at debug level"""
        if response.status_code < 200 or response.status_code > 299:
            self._raise_error(attempted_action or "Unknown action", response, url)
        else:
            log.debug("Request to %s successful.",
                      url or attempted_action or "Unknown")

    def _raise_error(self, msg, response: requests.Response, url):
        """Raises the correct type of exception."""
        error_map = {
            404: NBNotFoundError,
            400: NBBadRequestError
        }
        err = error_map.get(response.status_code) or NBResponseError
        raise err(msg, response.headers, response.text, url)

    def _authorize(self):
        """Gets Credentials with the ACCESS_TOKEN and authorises an AuthorizedSession.

        If this has already been done, does nothing."""
        if self.session is not None:
            return
        assert self.ACCESS_TOKEN is not None

        cred = Credentials(self.ACCESS_TOKEN)
        self.session = AuthorizedSession(cred)
        self.session.verify = False  # Disable SSL certificate verification


class NBResponseError(Exception):

    """
    Base class for all non-200 OK responses.
    Includes the following additional fields:
    header: the response headers
    body: the response body
    url: the requested url.
    """

    def __init__(self, msg, header, body, url):
        self.url = url
        self.header = header
        self.body = body
        print(url)
        print("Header: %s" % header)
        print("Body: %s" % body)
        Exception.__init__(self, msg)


class NBBadRequestError(NBResponseError):

    """Indicates a bad request"""
    pass


class NBNotFoundError(NBResponseError):

    """Generally indicates that a 404 error was returned...
    contains the header and body of the server response."""
    pass
