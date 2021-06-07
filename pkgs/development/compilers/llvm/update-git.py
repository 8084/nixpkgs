#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 nix

import csv
import fileinput
import json
import os
import re
import subprocess

from codecs import iterdecode
from datetime import datetime
from urllib.request import urlopen, Request


def get_latest_chromium_build():
    HISTORY_URL = 'https://omahaproxy.appspot.com/history?os=linux'
    print(f'GET {HISTORY_URL}')
    with urlopen(HISTORY_URL) as resp:
        builds = csv.DictReader(iterdecode(resp, 'utf-8'))
        for build in builds:
            if build['channel'] != 'dev':
                continue
            return build


def get_file_revision(revision, file_path):
    """Fetches the requested Git revision of the given Chromium file."""
    url = f'https://raw.githubusercontent.com/chromium/chromium/{revision}/{file_path}'
    with urlopen(url) as http_response:
        return http_response.read().decode()


def get_commit(ref):
    url = f'https://api.github.com/repos/llvm/llvm-project/commits/{ref}'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    request = Request(url, headers=headers)
    with urlopen(request) as http_response:
        return json.loads(http_response.read().decode())


def nix_prefetch_url(url, algo='sha256'):
    """Prefetches the content of the given URL."""
    print(f'nix-prefetch-url {url}')
    out = subprocess.check_output(['nix-prefetch-url', '--type', algo, '--unpack', url])
    return out.decode('utf-8').rstrip()


chromium_build = get_latest_chromium_build()
chromium_version = chromium_build['version']
print(f'chromiumDev version: {chromium_version}')
print('Getting LLVM commit...')
clang_update_script = get_file_revision(chromium_version, 'tools/clang/scripts/update.py')
clang_revision = re.search(r"^CLANG_REVISION = '(.+)'$", clang_update_script, re.MULTILINE).group(1)
clang_commit_short = re.search(r"llvmorg-[0-9]+-init-[0-9]+-g([0-9a-f]{8})", clang_revision).group(1)
release_version = re.search(r"^RELEASE_VERSION = '(.+)'$", clang_update_script, re.MULTILINE).group(1)
commit = get_commit(clang_commit_short)
date = datetime.fromisoformat(commit['commit']['committer']['date'].rstrip('Z')).date().isoformat()
version = f'unstable-{date}'
print('Prefetching source tarball...')
hash = nix_prefetch_url(f'https://github.com/llvm/llvm-project/archive/{commit["sha"]}.tar.gz')
print('Updating default.nix...')
default_nix = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'git/default.nix')
with fileinput.FileInput(default_nix, inplace=True) as f:
    for line in f:
        result = re.sub(r'^  release_version = ".+";', f'  release_version = "{release_version}";', line)
        result = re.sub(r'^  version = ".+";', f'  version = "{version}";', line)
        result = re.sub(r'^  rev = ".*";', f'  rev = "{commit["sha"]}";', result)
        result = re.sub(r'^    sha256 = ".+";', f'    sha256 = "{hash}";', result)
        print(result, end='')
