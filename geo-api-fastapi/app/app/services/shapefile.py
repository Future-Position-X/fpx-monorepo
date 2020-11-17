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


def shapefile_to_feature_collection(shapefile_path: str) -> dict:
    shp = geopandas.read_file(shapefile_path)
    shp.to_crs(epsg=4326, inplace=True)
    geojson = shp.to_json()
    return json.loads(geojson)


def jsonfile_to_feature_collection(jsonfile_path: str) -> dict:
    with open(jsonfile_path, "r") as file:
        return json.loads(file.read())


def merge_feature_collections(dst_fc: dict, src_fc: dict) -> None:
    for f in src_fc["features"]:
        dst_fc["features"].append(f)


other_shapefile_extensions = [
    ".shx",
    ".dbf",
    ".sbn",
    ".sbx",
    ".fbn",
    ".fbx",
    ".ain",
    ".aih",
    ".atx",
    ".ixs",
    ".mxs",
    ".prj",
    ".xml",
    ".cpg",
]


def convert_zip_to_feature_collection(upload_file: UploadFile) -> dict:
    path = save_upload_file_tmp(upload_file)
    zip = zipfile.ZipFile(path, "r")
    dir = tempfile.TemporaryDirectory().name
    zip.extractall(Path(dir))

    files = [
        os.path.join(dir, f)
        for f in os.listdir(dir)
        if os.path.isfile(os.path.join(dir, f))
    ]
    fc = {"type": "FeatureCollection", "features": []}

    for f in files:
        ext = Path(f).suffix.lower()

        if ext == ".shp":
            merge_feature_collections(fc, shapefile_to_feature_collection(f))
        elif ext == ".json" or ext == ".geojson":
            merge_feature_collections(fc, jsonfile_to_feature_collection(f))
        else:
            if not ext in other_shapefile_extensions:
                raise Exception("unknown file extension: " + ext)

    shutil.rmtree(dir)
    os.remove(path)
    return fc
