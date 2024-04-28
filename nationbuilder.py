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

        self.people = People(slug, api_key)
        self.tags = NBTags(slug, api_key)
        self.lists = Lists(slug, api_key)
        self.contacts = Contacts(slug, api_key)


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
    SITE_SLUG = os.getenv("SITE_SLUG")
    return NationBuilder(slug=SITE_SLUG, api_key=API_TOKEN)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='NationBuilder client')
    parser.add_argument("--person-id", type=int, help="The identifier for the person to retrieve")
    args = parser.parse_args()
    if args.person_id:
        print(f"Fetching user {args.person_id}")
        nb = get_nb_client_from_environment_variables()
        person = nb.people.get_person(person_id=args.person_id)
        print(json.dumps(person))
