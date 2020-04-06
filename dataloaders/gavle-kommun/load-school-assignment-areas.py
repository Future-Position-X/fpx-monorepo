from dotenv import load_dotenv
load_dotenv()
import requests, zipfile,json
from io import BytesIO
import os
import sys
import concurrent.futures

GIA_TOKEN = os.getenv("GIA_TOKEN")

collections = [
    {
        'name': 'school-assignment-areas',
        'url': 'https://catalog.gavle.se/store/1/resource/374',
        'filename': 'skolplaceringsomraden.json',
    },
    {
        'name': 'basemap-buildings',
        'url': 'https://catalog.gavle.se/store/1/resource/76',
        'filename': 'baskarta_byggnad.json',
    },
    {
        'name': 'basemap-building-types',
        'url': 'https://catalog.gavle.se/store/1/resource/76',
        'filename': 'baskarta_byggnadsbeteckning.json',
    }
]

def import_collection(collection):
    r = requests.get(collection['url'])

    z = zipfile.ZipFile(BytesIO(r.content))
    text = z.read(collection['filename'])
    json_obj = json.loads(text)
    wrapped_data = [{'data': json_obj}]
    headers = { 
        'authorization': 'Bearer ' + GIA_TOKEN,
        'content-type': 'application/json'
    }

    res = requests.post('https://api.gavleinnovationarena.se/2.0/collection/' + collection['name'], json=wrapped_data, headers=headers )
    return res

requested_collections = sys.argv[1:]
if len(requested_collections) == 0:
    request_collections = collections
else:
    request_collections = [col for col in collections if col['name'] in requested_collections]

print(request_collections)

with concurrent.futures.ProcessPoolExecutor() as executor:
        for collection, status in zip(request_collections, executor.map(import_collection, request_collections)):
            print('%s returned: %s' % (collection['name'], status))