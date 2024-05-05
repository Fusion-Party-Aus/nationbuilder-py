from typing import Optional

import nb_api


class Blog(nb_api.NationBuilderApi):
    def get_blogs(self, site_slug=nb_api.SITE_SLUG, limit: Optional[int] = 100):
        # There can be multiple blogs in a site − each is essentially a topic
        self._authorize()
        response = self.session.get(self.BLOGS_URL.format(site_slug), headers=self.HEADERS, params={"limit": limit})
        self._check_response(response, "Get blogs", response.url)
        return response.json()

    def create_blog(self, site_slug, blog):
        self._authorize()
        response = self.session.post(self.BLOGS_URL.format(site_slug), headers=self.HEADERS, json={"blog": blog})
        self._check_response(response, "Create blog", response.url)
        if response.ok:
            return response.json()
        else:
            return None

    def get_blog_posts(self, site_slug: str, blog_id: int, limit: Optional[int] = 100):
        # An actual article within a blog (a topic) − but only an excerpt! NationBuilder's API seems
        self._authorize()
        response = self.session.get(self.BLOG_POSTS_URL.format(site_slug, int(blog_id)), headers=self.HEADERS, params={"limit": limit})
        self._check_response(response, "Get blog posts", response.url)
        return response.json()

    def get_next_blog_posts(self, url, limit: Optional[int] = 100):
        response = self.session.get(url, headers=self.HEADERS, params={"limit": limit})
        self._check_response(response, "Get blog posts", url)
        return response.json()

    def create_blog_post(self, site_slug: str, blog_id: int, blog_post: dict):
        self._authorize()
        url = self.BLOG_POSTS_URL.format(site_slug, blog_id)
        print(f"Creating {blog_post}")
        response = self.session.post(url, headers=self.HEADERS, json={"blog_post": blog_post})
        self._check_response(response, "Create blog post", response.url)
        if response.ok:
            return response.json()
        else:
            return None
