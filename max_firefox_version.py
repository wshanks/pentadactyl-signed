#!/usr/bin/env python
'''Script to pull latest Firefox version string from Mozilla'''

import re

from bs4 import BeautifulSoup
import requests


def is_firefox(items):
    '''Check if list of li tags refers to Firefox'''
    for item in items:
        # One of the list items in the div contains the GUID
        if re.search('ec8030f7-c20a-464f-9b0e-13a3a9e97384', item.get_text()):
            return True

    return False


def get_versions(items):
    '''Get list of version from li tags referring to Firefox'''
    for item in items:
        # The list item with the versions starts with "Versions:"
        if re.match('Versions:', item.get_text()):
            versions_str = item.code.get_text()
            return [v.strip() for v in versions_str.split(',')]


def main():
    '''Main logic'''
    req = requests.get(
        'https://addons.mozilla.org/en-US/firefox/pages/appversions/')
    soup = BeautifulSoup(req.content, 'html.parser')

    # Blocks with valid versions are divs of class appversion prose
    version_sets = [s for s in soup.find_all('div', 'appversion prose')]

    for ver_set in version_sets:
        items = ver_set('li')
        if is_firefox(items):
            version_list = get_versions(items)

    # Versions ordered oldest to newest
    version_list.reverse()
    for version in version_list:
        # Match newest version without prerelease characters in string
        if re.match(r'^[0-9\.]+$', version):
            if int(version.split('.')[0]) < 57:
                # Get the latest release lest than 57
                print(version)
                return

    raise RuntimeError('No version strings found')


if __name__ == '__main__':
    main()
