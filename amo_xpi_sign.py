#!/usr/bin/env python3
'''Script to sign a Firefox xpi'''

import argparse
import re
import shutil
import subprocess

TIMEOUT = 10*60*1000


def handle_arguments():
    '''Handle command line arguments'''
    parser = argparse.ArgumentParser(description=('Sign .xpi file on '
                                                  'mozilla.org'))
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
    parser.add_argument('--xpi', '-x', type=str, required=True,
                        help='.xpi file to be signed')

    return vars(parser.parse_args())


def sign(xpi, key, secret, output=None):
    '''Upload xpi file for signing and then download the signed xpi if
    successful'''
    jpm_cmd = ['jpm', 'sign', '--api-key', key, '--api-secret', secret,
               '--xpi', xpi, '--timeout', str(TIMEOUT)]
    proc = subprocess.run(jpm_cmd, stdout=subprocess.PIPE,
                          universal_newlines=True)

    stdout = proc.stdout.splitlines()

    if re.match('JPM [info] SUCCESS', stdout[-1]):
        signed_xpi = re.match(r'JPM \[info\]\s+(.*\.xpi)', stdout[-2]).group(1)
        if output:
            shutil.move(signed_xpi, output)
            signed_xpi = output
    else:
        raise RuntimeError(proc.stdout)

    return signed_xpi


def main():
    '''Main logic'''
    args = handle_arguments()

    sign(**args)

if __name__ == '__main__':
    main()
