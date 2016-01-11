#!/usr/bin/env python3
'''Convert a tag to a GitHub release and add a file download to it'''

import os

import requests
from uritemplate import expand


def create_release(api_url, token, version):
    '''Create GitHub relase for an existing tag'''
    release_json = get_release_json(api_url, version)

    if not release_json:
        headers = {'Authorization': 'token {}'.format(token)}
        req = requests.post(api_url,
                            json={'tag_name': version},
                            headers=headers)
        req.raise_for_status()
        release_json = get_release_json(api_url, version)

    return release_json


def get_release_json(api_url, version):
    '''Get release json response'''
    tag_url = api_url + '/tags/{version}'.format(version=version)

    req = requests.get(tag_url)

    release_json = req.json()

    if 'message' in release_json and release_json['message'] == 'Not Found':
        return False

    return release_json


def upload_file(url, token, filepath, content_type):
    '''Upload file to GitHub release'''
    headers = {'Content-Type': content_type,
               'Authorization': 'token {}'.format(token)}
    req = requests.post(url, headers=headers, data=open(filepath, 'rb'))
    req.raise_for_status()


def main():
    '''Main logic'''
    import argparse
    parser = argparse.ArgumentParser('Create GitHub relase')
    parser.add_argument('--token', '-t', required=True,
                        help='GitHub authentication token')
    parser.add_argument('--user', '-u', required=True,
                        help='GitHub user account')
    parser.add_argument('--repo', '-r', required=True,
                        help='GitHub repo name')
    parser.add_argument('--version', '-v', required=True,
                        help='Version to create')
    parser.add_argument('--file', '-f',
                        help='File to upload to release')
    parser.add_argument('--content-type', '-c',
                        help='Content type of file')

    args = parser.parse_args()

    api_url = 'https://api.github.com/repos/{user}/{repo}/releases'
    api_url = api_url.format(user=args.user, repo=args.repo)

    # Create release
    release_json = create_release(api_url, args.token, args.version)

    # Upload file
    if args.file:
        upload_url = expand(release_json['upload_url'],
                            {'name': os.path.basename(args.file)})
        upload_file(upload_url, args.token, args.file, args.content_type)


if __name__ == '__main__':
    main()
