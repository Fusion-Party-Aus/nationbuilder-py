# nationbuilder.py ---
#
# Filename: nationbuilder.py
# Description: Main Entry point.
# Author: Niklas Rehfeld

"""
The  NationBuilder object is used as a way of accessing a NationBuilder Nation.
It contains attributes for accessing the various API endpoints.

Example usage:

# create a NationBuilder object that accesses the slug.nationbuilder.com nation
my_site = nbpy.nationbuilder.NationBuilder("slug", MY_API_KEY)

# get person with ID=123
ppl = my_site.people.get_person(123)

# retrieve the people in list 5
list_five = my_site.lists.get_list(5)

"""
import argparse
import json
import os

from blog import Blog
from nb_api import SITE_SLUG
from pages import Pages
from people import People
from tags import NBTags
from lists import Lists
from contacts import Contacts


class NationBuilder(object):

    """
    Entry point to nationbuilder APIs.

    Public attributes:
        people : nbpy.people.People instance for accessing people API
        tags : nbpy.tags.NBTags instance for accessing People Tags API
        lists : nbpy.lists.NBList instance for accessing Lists API
    """

    def __init__(self, slug, api_key):
        super(NationBuilder, self).__init__()
        self.blog_posts = Blog(slug, api_key)
        self.contacts = Contacts(slug, api_key)
        self.lists = Lists(slug, api_key)
        self.pages = Pages(slug, api_key)
        self.people = People(slug, api_key)
        self.tags = NBTags(slug, api_key)


def from_file(filename):
    """
    Factory method that creates a NationBuilder instance from a file containing
    the nation slug and the api key.

    The format of the file is as follows:

        slug: slug
        api_key: key

    pretty simple I reckon.
    """
    with open(filename, 'r') as creds:
        slug = None
        key = None
        for line in creds:
            parts = line.split(":")
            if parts[0].strip() == 'slug':
                slug = parts[1].strip()
            elif parts[0].strip() == 'api_key':
                key = parts[1].strip()
        if slug is not None and key is not None:
            return NationBuilder(slug, key)
        return None


def get_nb_client_from_environment_variables() -> NationBuilder:
    API_TOKEN = os.getenv("NATIONBUILDER_API_TOKEN")
    NATION_SLUG = os.getenv("NATION_SLUG")
    return NationBuilder(slug=NATION_SLUG, api_key=API_TOKEN)


def handle_people(args):
    nb = get_nb_client_from_environment_variables()
    person = nb.people.get_person(person_id=args.person_id)
    print(json.dumps(person))


def handle_pages(args):
    nb = get_nb_client_from_environment_variables()
    pages = None
    next_page_url = None
    destination_site_slug = getattr(args, 'destination_site_slug', None)
    while pages is None or (pages["results"] and pages["next"] and destination_site_slug):
        if next_page_url:
            pages = nb.pages.get_next_pages(next_page_url)
        else:
            pages = nb.pages.get_pages(site_slug=getattr(args, "site_slug", ""))
        if destination_site_slug:
            for page in pages["results"]:
                created = nb.pages.create_page(site_slug=destination_site_slug, page=page)
                if created:
                    print(f"Created {destination_site_slug}: {page['slug']} ({page['name']})")
                break
        break
    print(json.dumps(pages))
    return pages


def handle_blog_posts(args):
    nb = get_nb_client_from_environment_variables()
    blog_posts = None
    next_page_url = None
    destination_site_slug = getattr(args, 'destination_site_slug', None)
    while blog_posts is None or (blog_posts["results"] and blog_posts["next"] and destination_site_slug):
        if next_page_url:
            blog_posts = nb.blog_posts.get_next_blog_posts(next_page_url)
        else:
            blog_posts = nb.blog_posts.get_blog_posts(site_slug=getattr(args, "site_slug", ""))
        if destination_site_slug:
            for page in blog_posts["results"]:
                created = nb.blog_posts.create_blog_post(site_slug=destination_site_slug, blog_post=page)
                if created:
                    print(f"Created {destination_site_slug}: {page['slug']} ({page['name']})")
                break
        break
    print(json.dumps(blog_posts))
    return blog_posts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='NationBuilder client')
    subparsers = parser.add_subparsers(dest="command")
    people_parser = subparsers.add_parser("people")
    people_parser.add_argument("--person-id", type=int, help="The identifier for the person to retrieve")
    people_parser.set_defaults(func=handle_people)
    # todo: copy basic pages from one site to another.
    page_parser = subparsers.add_parser("pages")
    page_parser.add_argument("--site-slug", default=SITE_SLUG, type=str, help="The site to consult for pages")
    page_parser.add_argument("--destination-site-slug", default=SITE_SLUG, type=str,
                             help="Copy the original pages to this destination")
    page_parser.set_defaults(func=handle_pages)
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()