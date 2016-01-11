#!/usr/bin/env python3
'''Script to sign a Firefox xpi'''

import argparse
from collections import namedtuple
import os
import random
import re
import time

import requests
from requests_jwt import JWTAuth


API_URL = 'https://addons.mozilla.org/api/v3/addons/'
TIMEOUT = 90


def handle_arguments():
    '''Handle command line arguments'''
    parser = argparse.ArgumentParser(description=('Sign .xpi file on '
                                                  'mozilla.org'))
    parser.add_argument('--addon-id', '-i', type=str,
                        help='Addon''s id')
    parser.add_argument('--key', '-k', type=str, required=True,
                        help='AMO API key')
    parser.add_argument('--output', '-o', type=str,
                        help=('Target file or directory to save signed .xpi '
                              'file to. The default behavior is to save in '
                              'the same directory as the unsigned xpi with '
                              '\'-signed\' appended to the file '
                              'name (before the \'.xpi\' extension). If a '
                              'directory is given, this default name is used '
                              'to save the .xpi file in that directory.'))
    parser.add_argument('--secret', '-s', type=str, required=True,
                        help='AMO secret key')
    parser.add_argument('--version', '-v', type=str,
                        help='Version number string for add-on file')
    parser.add_argument('--xpi', '-x', type=str, required=True,
                        help='.xpi file to be signed')

    return vars(parser.parse_args())


def create_auth(key, secret):
    '''Create auth generator for requests'''
    auth = JWTAuth(secret, alg='HS256', header_format='JWT %s')
    auth.add_field('iss', key)
    auth.add_field('jti', lambda x: random.random())
    auth.add_field('iat', lambda x: int(time.time()))
    auth.expire(60)

    return auth


def lookup_id_version(xpi):
    '''Extract addon id and version from xpi's install.rdf'''
    from zipfile import ZipFile
    from bs4 import BeautifulSoup as BS

    with ZipFile(xpi) as xpi_zip:
        soup = BS(xpi_zip.open('install.rdf').read(), 'lxml')

    def get_prop(name):
        '''Get rdf property of Description (they can be formatted as either
        HTML attributes or properties)'''
        prop = soup.find(name)
        if not prop:
            desc = soup.find(re.compile('description', flags=re.I))
            prop = str(desc.attrs['em:' + name])
        else:
            prop = prop.text()

        return prop

    addon_props = namedtuple('AddonProperties', ['id', 'version'])
    return addon_props(get_prop('id'), get_prop('version'))


# pylint: disable=too-many-arguments
def sign(xpi, key, secret, addon_id=None, version=None, output=None):
    '''Upload xpi file for signing and then download the signed xpi if
    successful'''
    if not addon_id or not version:
        addon_id, version = lookup_id_version(xpi)

    auth = create_auth(key, secret)
    url = API_URL + '{id}/versions/{version}/'.format(id=addon_id,
                                                      version=version)

    # Upload
    req = requests.put(url, auth=auth,
                       files={'upload': open(xpi, 'rb')})
    # Stop for any error other than addon already being uploaded
    print(req.json())
    if req.status_code != 409:
        req.raise_for_status()
        url = req.json()['url']

    # Check and wait
    start = time.time()
    while time.time() - start < TIMEOUT:
        req = requests.get(url, auth=auth)
        req.raise_for_status()

        status = req.json()
        if status['active']:
            break
        else:
            time.sleep(2)

    if not status['active']:
        raise RuntimeError('Timeout reached waiting for addon signing')

    # Download
    req = requests.get(status['files'][0]['download_url'], auth=auth)
    req.raise_for_status()
    signed_xpi = format_output_path(xpi, output)
    with open(signed_xpi, 'wb') as output_file:
        output_file.write(req.content)

    return signed_xpi
# pylint: enable=too-many-arguments


def format_output_path(xpi, output):
    '''Create default output file path from xpi file path if output is None'''
    if output:
        return output

    path, xpi_file = os.path.split(xpi)
    xpi_root, xpi_ext = os.path.splitext(xpi_file)
    return os.path.join(path, xpi_root + '-signed' + xpi_ext)


def main():
    '''Main logic'''
    args = handle_arguments()

    sign(**args)

if __name__ == '__main__':
    main()
