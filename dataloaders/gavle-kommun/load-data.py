import json
import zipfile
import requests
import concurrent.futures
import sys
import os
import gzip
import math
from io import BytesIO
import time

from dotenv import load_dotenv
load_dotenv()

GIA_TOKEN = os.getenv("GIA_TOKEN")

collections = [
    {
        'name': 'deso',
        'url': 'data/deso.geojson.gz',
        'uuid': '916d7821-a159-4c5a-8e54-e3e952cd8512',
        'is_file': True,
        'batch_size': 1000
    },
    {
        'name': 'sverige-kommuner',
        'url': 'data/sverige-kommuner.geojson.gz',
        'uuid': '457bcd8e-b181-43b6-83d3-30ff906057ac',
        'is_file': True,
        'batch_size': 1000
    },
    {
        'name': 'sverige-lan',
        'url': 'data/sverige-lan.geojson.gz',
        'uuid': 'f36fa6fb-f18d-42a1-9db7-c087bd0d01e5',
        'is_file': True,
        'batch_size': 1000
    },
    {
        'name': 'obstacles',
        'url': 'data/obstacles.geojson.gz',
        'uuid': '5cbb09a7-57a5-4641-849a-f0c36ed24bb0',
        'is_file': True,
        'batch_size': 1000
    },
    {
        'name': 'school-assignment-areas',
        'url': 'https://catalog.gavle.se/store/1/resource/374',
        'filename': 'skolplaceringsomraden.json',
        'uuid': '4c2d3a7d-53ac-42b5-828e-a509d277e0db',
        'batch_size': 1000
    },
    {
        'name': 'basemap-buildings',
        'url': 'https://catalog.gavle.se/store/1/resource/76',
        'filename': 'baskarta_byggnad.json',
        'uuid': '08f8a8e1-f13a-4b61-9d27-4073aabfc976',
        'batch_size': 1000
    },
    {
        'name': 'basemap-building-types',
        'url': 'https://catalog.gavle.se/store/1/resource/76',
        'filename': 'baskarta_byggnadsbeteckning.json',
        'uuid': '864eebb6-07b1-4d76-a553-745484454cd6',
        'batch_size': 1000
    },
    {
        'name': 'comprehensive-plans-boundaries',
        'url': 'https://catalog.gavle.se/store/1/resource/379',
        'filename': 'oversiktsplan_granser.json',
        'uuid': '2663d60c-0c32-489f-8554-504a765ccc2b',
        'batch_size': 1000
    },
    {
        'name': 'control-points-height',
        'url': 'https://catalog.gavle.se/store/1/resource/355',
        'filename': 'Stompunkter_hojd.json',
        'uuid': '4ae1140f-3f68-4074-a278-ed21113190ab',
        'batch_size': 1000
    },
    {
        'name': 'control-points-plane',
        'url': 'https://catalog.gavle.se/store/1/resource/355',
        'filename': 'Stompunkter_plan.json',
        'uuid': 'b774b6e7-b186-4b7a-acfa-fb5b78aaa155',
        'batch_size': 1000
    },
    {
        'name': 'historical-signs',
        'url': 'https://catalog.gavle.se/store/1/resource/369',
        'filename': 'historiska_skyltar.json',
        'uuid': '57fefc9f-d428-4629-8d34-adfc9e94250d',
        'batch_size': 1000
    },
    {
        'name': 'outdoor-gyms',
        'url': 'https://catalog.gavle.se/store/1/resource/360',
        'filename': 'utegym.json',
        'uuid': 'b039f47a-4f3e-4e78-aff0-30ab4e6cc3ed',
        'batch_size': 1000
    },
    {
        'name': 'parking-meters',
        'url': 'https://catalog.gavle.se/store/1/resource/364',
        'filename': 'parkeringsautomater-json.json',
        'uuid': '270352c3-2d2b-4e03-9460-96eb48dec846',
        'batch_size': 1000
    },
    {
        'name': 'accessibility-main-walkway',
        'url': 'https://catalog.gavle.se/store/1/resource/337',
        'filename': 'tillganglighet_huvudgangstrak.json',
        'uuid': '1166be6b-23bd-4d7b-b9e6-e0b88a135e60',
        'batch_size': 1000
    },
    {
        'name': 'accessibility-inventoried-areas',
        'url': 'https://catalog.gavle.se/store/1/resource/337',
        'filename': 'tillganglighet_inventerade_omraden.json',
        'uuid': '903a99d1-db26-4760-9724-47510d09cb21',
        'batch_size': 1000
    },
    {
        'name': 'accessibility-parking',
        'url': 'https://catalog.gavle.se/store/1/resource/337',
        'filename': 'tillganglighet_parkering_rorelsehindrad.json',
        'uuid': '8504aee0-d822-4a9e-ac2f-4840ed64c644',
        'batch_size': 1000
    },
    {
        'name': 'accessibility-passages',
        'url': 'https://catalog.gavle.se/store/1/resource/337',
        'filename': 'tillganglighet_passager.json',
        'uuid': '7c8b9963-f80d-4049-b5f5-dfb7edaeb975',
        'batch_size': 1000
    },
    {
        'name': 'accessibility-benches',
        'url': 'https://catalog.gavle.se/store/1/resource/337',
        'filename': 'tillganglighet_bankar.json',
        'uuid': '885e59a4-1fd3-4691-8ba0-b459a7854595',
        'batch_size': 1000
    },
    {
        'name': 'accessibility-lighting',
        'url': 'https://catalog.gavle.se/store/1/resource/337',
        'filename': 'tillganglighet_belysning.json',
        'uuid': '45acf68d-4402-49c7-a909-231ce09bd44a',
        'batch_size': 1000
    },
    {
        'name': 'accessibility-bus-stops',
        'url': 'https://catalog.gavle.se/store/1/resource/337',
        'filename': 'tillganglighet_busshallplatser.json',
        'uuid': '304f280f-01da-454c-b08a-93d40d85fa14',
        'batch_size': 1000
    },
    {
        'name': 'life-saving-appliances',
        'url': 'https://catalog.gavle.se/store/1/resource/325',
        'filename': 'livraddningsutrustning.json',
        'uuid': 'fc82bf5a-12a9-4c40-abd5-8b7319147d7f',
        'batch_size': 1000
    },
    {
        'name': 'snow-removal',
        'url': 'https://catalog.gavle.se/store/1/resource/304',
        'filename': 'snorojninghalkbekampning.json',
        'uuid': 'bcaaa89d-3541-4344-8478-ff941a57611b',
        'batch_size': 1000
    },
    {
        'name': 'toboggan-hills',
        'url': 'https://catalog.gavle.se/store/1/resource/297',
        'filename': 'pulkabackar.json',
        'uuid': '9746f477-cd28-4c8e-8ad3-16972ad7764e',
        'batch_size': 1000
    },
    {
        'name': 'ice-skating-rinks',
        'url': 'https://catalog.gavle.se/store/1/resource/299',
        'filename': 'isbanor.json',
        'uuid': '81157c06-3fab-4c71-9f8d-f09b39649c90',
        'batch_size': 1000
    },
    {
        'name': 'tree-care',
        'url': 'https://catalog.gavle.se/store/1/resource/289',
        'filename': 'tradskotsel.json',
        'uuid': 'a0cb26fe-6193-45d9-bcab-0aa44c2f0c99',
        'batch_size': 1000
    },
    {
        'name': 'gravel-surfaces',
        'url': 'https://catalog.gavle.se/store/1/resource/284',
        'filename': 'grusytor.json',
        'uuid': '389770a6-4ca9-4294-9357-7e92ecd7ec3b',
        'batch_size': 1000
    },
    {
        'name': 'aerial-photo-objects',
        'url': 'https://catalog.gavle.se/store/1/resource/279',
        'filename': 'Foto_objekt.json',
        'uuid': '54a25f28-a8d6-44e7-8d71-5c09186dc198',
        'batch_size': 1000
    },
    {
        'name': 'aerial-photos-oblique-images',
        'url': 'https://catalog.gavle.se/store/1/resource/279',
        'filename': 'Foto_snedbilder.json',
        'uuid': 'fc216287-a265-4529-94ae-64e4d8a5bf84',
        'batch_size': 1000
    },
    {
        'name': 'waste-containers',
        'url': 'https://catalog.gavle.se/store/1/resource/273',
        'filename': 'papperskorgar.json',
        'uuid': '1b57c937-67d1-46ec-9bd3-6ec1650861ab',
        'batch_size': 1000
    },
    {
        'name': 'basemap-details-line-objects',
        'url': 'https://catalog.gavle.se/store/1/resource/96',
        'filename': 'baskarta_linjeobjekt.json',
        'uuid': '7d4518ef-ac61-4555-bcc7-70c00a2cc0c7',
        'batch_size': 1000
    },
    {
        'name': 'basemap-details-point-objects',
        'url': 'https://catalog.gavle.se/store/1/resource/96',
        'filename': 'baskarta_punktobjekt.json',
        'uuid': '7660c927-41e2-4ce1-8b41-cee8c1311287',
        'batch_size': 1000
    },
    {
        'name': 'basemap-roads',
        'url': 'https://catalog.gavle.se/store/1/resource/94',
        'filename': 'baskarta_vag.json',
        'uuid': 'c7e2ff41-ba64-4a09-be00-1f4be7933934',
        'batch_size': 1000
    },
    {
        'name': 'basemap-railroads',
        'url': 'https://catalog.gavle.se/store/1/resource/94',
        'filename': 'baskarta_jarnvag.json',
        'uuid': '28bc1736-5975-4728-8821-4285427026a6',
        'batch_size': 1000
    },
    {
        'name': 'basemap-water',
        'url': 'https://catalog.gavle.se/store/1/resource/92',
        'filename': 'baskarta_vatten.json',
        'uuid': '38d0d300-669a-42bd-895a-82b1b89eea79',
        'batch_size': 1000
    },
    {
        'name': 'basemap-water-line-objects',
        'url': 'https://catalog.gavle.se/store/1/resource/92',
        'filename': 'baskarta_vattenobjekt_linje.json',
        'uuid': '08f924ee-ae39-46f6-81c5-023f0fd4302e',
        'batch_size': 1000
    },
    {
        'name': 'basemap-water-point-objects',
        'url': 'https://catalog.gavle.se/store/1/resource/92',
        'filename': 'baskarta_vattenobjekt_punkt.json',
        'uuid': 'aef36a61-b15b-4f36-be0e-d2602d294578',
        'batch_size': 1000
    },
    {
        'name': 'basemap-water-surface-objects',
        'url': 'https://catalog.gavle.se/store/1/resource/92',
        'filename': 'baskarta_vattenobjekt_yta.json',
        'uuid': '89eab165-727d-46be-83ae-8e631dc08c53',
        'batch_size': 1000
    },
    {
        'name': 'basemap-shoreline',
        'url': 'https://catalog.gavle.se/store/1/resource/92',
        'filename': 'baskarta_strandlinje.json',
        'uuid': 'c7a9937e-2643-433b-a4f1-bb86b766c803',
        'batch_size': 1000
    },
    {
        'name': 'basemap-properties',
        'url': 'https://catalog.gavle.se/store/1/resource/86',
        'filename': 'baskarta_fastighet.json',
        'uuid': '1c51e8c6-78ce-4c60-a1ea-f8234e4e28aa',
        'batch_size': 1000
    },
    {
        'name': 'basemap-properties-boundary-point',
        'url': 'https://catalog.gavle.se/store/1/resource/86',
        'filename': 'baskarta_granspunkt.json',
        'uuid': '5fdd3baf-ab87-40d4-8250-2c60d020578a',
        'batch_size': 1000
    },
    {
        'name': 'basemap-properties-municipal-boundary',
        'url': 'https://catalog.gavle.se/store/1/resource/86',
        'filename': 'baskarta_kommungrans.json',
        'uuid': 'c76dc36e-adbe-4f01-9a27-916599045a62',
        'batch_size': 1000
    },
    {
        'name': 'basemap-properties-region',
        'url': 'https://catalog.gavle.se/store/1/resource/86',
        'filename': 'baskarta_trakt.json',
        'uuid': '41f6f666-771f-4ccc-8782-61f297fe8cda',
        'batch_size': 1000
    },
    {
        'name': 'basemap-addresses',
        'url': 'https://catalog.gavle.se/store/1/resource/88',
        'filename': 'baskarta_adress.json',
        'uuid': '2609dd38-2af4-4438-8c62-a0b7150678be',
        'batch_size': 1000
    },
    {
        'name': 'basemap-elevations',
        'url': 'https://catalog.gavle.se/store/1/resource/90',
        'filename': 'baskarta_hojder.json',
        'uuid': 'fc9b4a8b-05be-4c90-8e47-f8b5a8e6dbc3',
        'batch_size': 1000
    }
]


def import_collection(collection):
    print("processing dataset: ", collection["name"])

    is_file = collection.get('is_file', False)

    if is_file:
        with gzip.open(collection['url'], "r") as file:
            json_obj = json.loads(file.read())
    else:
        r = requests.get(collection['url'])
        z = zipfile.ZipFile(BytesIO(r.content))
        text = z.read(collection['filename'])
        json_obj = json.loads(text)

    headers = {
        'Authorization': 'Bearer ' + GIA_TOKEN,
        'Content-Type': 'application/geojson',
        'Accept': 'application/geojson'
    }

    length = len(json_obj['features'])
    offset = 0
    while offset < length:
        start_time = time.time()
        batch_size = min(length - offset, collection['batch_size'])

        fc = {
                "type": "FeatureCollection",
                "features": json_obj['features'][offset:offset+batch_size]
        }

        url = 'http://dev.gia.fpx.se/collections/' + collection['uuid'] + '/items'

        if offset == 0:
            res = requests.post(url, json=fc, headers=headers)
        else:
            res = requests.put(url, json=fc, headers=headers)
        print("--- dataset %s, batch %s, %s seconds ---" % (collection["name"], offset, (time.time() - start_time)))
        offset += batch_size
    return res


requested_collections = sys.argv[1:]
if len(requested_collections) == 0:
    request_collections = collections
else:
    request_collections = [
        col for col in collections if col['name'] in requested_collections]

print(request_collections)

#with concurrent.futures.ThreadPoolExecutor() as executor:
    #for collection, status in zip(request_collections, executor.map(import_collection, request_collections)):
        #print('%s returned: %s' % (collection['name'], status))

for collection in request_collections:
    response = import_collection(collection)
    print('%s returned: %s' % (collection['name'], response))
