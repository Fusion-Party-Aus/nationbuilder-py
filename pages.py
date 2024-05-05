from typing import TypedDict, Optional

from nb_api import NationBuilderApi

# todo: generate TypedDicts from https://github.com/nationbuilder/api_spec/blob/master/spec.json

class PageResponse(TypedDict):
    next: str
    prev: Optional[str]
    results: list


class Pages(NationBuilderApi):
    """
    Used to get at the People API

    See https://nationbuilder.com/basic_pages_api for info on the data returned
    """

    def __init__(self, slug, token):
        super(Pages, self).__init__(slug, token)

    def get_sites(self):
        self._authorize()
        url = self.SITES_URL
        response = self.session.get(url, headers=self.HEADERS)
        self._check_response(response, "Get sites", url)
        return response.json()

    def get_pages(self, site_slug: str, limit: Optional[int] = 100):
        self._authorize()
        url = self.PAGES_URL.format(site_slug)
        response = self.session.get(url, headers=self.HEADERS, params={"limit": limit})
        self._check_response(response, "Get pages", url)
        return response.json()

    def get_next_pages(self, url, limit: Optional[int] = 100):
        response = self.session.get(url, headers=self.HEADERS, params={"limit": limit})
        self._check_response(response, "Get pages", url)

    def create_page(self, site_slug: str, page: dict, page_type="basic_page"):
        self._authorize()
        url = self.PAGES_URL.format(site_slug)
        response = self.session.post(url, headers=self.HEADERS, json={page_type: page})
        if response.ok:
            return response.json()
        else:
            return None
