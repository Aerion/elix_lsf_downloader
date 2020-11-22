#!/usr/bin/env python3

from typing import Pattern
from urllib.parse import urljoin

import json
import os
import pathlib
import re
import requests
import shutil
import sys


OUTPUT_FOLDER = 'downloads'


class ElixClient:
    api_url: str
    api_key: str
    video_url: str

    def __init__(self):
        app_bundle_data = requests.get("https://dico.elix-lsf.fr/js/app.bundle.js").text

        self.api_url = self._extract_regex_group(r'"apiUrl":"([^"]+)', app_bundle_data, 'api url')
        self.api_key = self._extract_regex_group(r'apikey=(\w+)"', app_bundle_data, 'api key')
        self.video_url = self._extract_regex_group(r'"videosUrl":"([^"]+)', app_bundle_data, 'video base url')

    def _extract_regex_group(self, pattern: Pattern, haystack: str, friendly_name: str):
        match = next(re.finditer(pattern, haystack))
        if match is None:
            raise Exception(f"Couldn't find {friendly_name} from app.bundle.js")
        return match.group(1)

    def get_video_url(self, word: str):
        url = urljoin(self.api_url, 'words')
        resp = requests.get(url, params={'apikey': self.api_key, 'q': word}).json()

        if resp['total'] == 0:
            raise Exception(f'Unknown word "{word}"')

        details = resp['data'][0]
        meanings = details.get('meanings', [])
        if len(meanings) == 0:
            raise Exception(f'Word "{word}" doesn\'t have any known meanings')

        word_signs = meanings[0].get('wordSigns', [])
        if len(word_signs) == 0:
            raise Exception(f'Word "{word}" doesn\'t have any known signs')

        return urljoin(self.video_url, word_signs[0]['uri'])


def download_file(url: str, filename: str):
    with requests.get(url, stream=True) as resp:
        with open(filename, 'wb') as out:
            shutil.copyfileobj(resp.raw, out)



os.makedirs(OUTPUT_FOLDER, exist_ok=True)
client = ElixClient()

if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help'):
    print(f'usage: {sys.argv[0]} <word...>')
    exit(0)

for word in sys.argv[1:]:
    print(f'Processing word {word}')
    try:
        url = client.get_video_url(word)
        ext = url.split('.')[-1]
        filename = pathlib.Path(OUTPUT_FOLDER).joinpath(f'{word}.{ext}')
        download_file(url, filename)
    except Exception as ex:
        print(f'Error processing {word}: {ex}')