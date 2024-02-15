#!/usr/bin/env python3

import os
import pathlib
import shutil
import sys
import requests


OUTPUT_FOLDER = 'downloads'


def download_file(url: str, filename: str):
    with requests.get(url, stream=True) as resp:
        with open(filename, 'wb') as out:
            shutil.copyfileobj(resp.raw, out)


os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help'):
    print(f'usage: {sys.argv[0]} <word...>')
    exit(0)

for word in sys.argv[1:]:
    print(f'Processing word {word}')
    try:
        json_response = requests.get(f'https://api.elix-lsf.fr/words?q={word}').json()
        result_list = [result for result in json_response['data'] if result['typology'] != 'n.prop.' and result['meanings'] and result['meanings'][0]['wordSigns']]
        if not result_list:
            print(f'\tNo result for word {word}')
            continue

        for result in result_list:
            url = 'https://www.elix-lsf.fr/IMG/' + result['meanings'][0]['wordSigns'][0]['uri']
            ext = url.split('.')[-1]
            filename = pathlib.Path(OUTPUT_FOLDER).joinpath(f'{result["name"]}_{result["typology"]}{ext}')

            download_file(url, filename)
    except Exception as ex:
        print(f'\tError processing {word}: {ex}')
        raise
