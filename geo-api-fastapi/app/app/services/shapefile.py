import zipfile
import tempfile
import glob
import shutil
import os
from pathlib import Path
from fastapi import UploadFile
from tempfile import NamedTemporaryFile
import geopandas
import json

def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path

def convert_shapefile_to_geojson(upload_file: UploadFile):
    path = save_upload_file_tmp(upload_file)
    zip = zipfile.ZipFile(path, 'r')
    dir = tempfile.TemporaryDirectory().name
    zip.extractall(Path(dir))
    shapefile = glob.glob(dir + '/*.shp')[0]
    shp = geopandas.read_file(shapefile)
    shp.to_crs(epsg=4326, inplace=True)
    geojson = shp.to_json()
    shutil.rmtree(dir)
    os.remove(path)
    return json.loads(geojson)