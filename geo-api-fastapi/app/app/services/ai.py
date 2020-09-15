import concurrent.futures
import os
import random
from datetime import datetime, timedelta

import joblib
import pandas as pd
from geoalchemy2.shape import to_shape

from app.models import Item as ItemDB, Feature
from app.models.ai.data_predictors.sensor_prediction import SensorPrediction
from app.models.ai.data_preperation.gcs_sensor_data import SensorData
from app.models.ai.polygon_environment import PolygonEnvironment
from app.models.ai.walking_agent import WalkingAgent


def generate_agents(points, n_agents, pathlength):
    return [WalkingAgent(random.choice(points), pathlength) for a in range(n_agents)]


def move_agent(a):
    global env
    a.move(env)
    return a


def generate_paths_from_points(
    points_collection_uuid,
    obstacles_collection_uuid,
    store_uuid,
    n_agents,
    steps,
    provider_uuid,
    filters,
):
    global env
    starting_points = ItemDB.find_readable_by_collection_uuid(
        provider_uuid, points_collection_uuid, filters
    )
    obstacles = ItemDB.find_readable_by_collection_uuid(
        provider_uuid, obstacles_collection_uuid, filters
    )

    obstacle_features = [
        Feature(
            to_shape(item.geometry), item.properties, str(item.uuid)
        ).__geo_interface__
        for item in obstacles
        if item.geometry is not None
    ]
    env = PolygonEnvironment(obstacle_features)

    starting_points_features = [
        Feature(
            to_shape(item.geometry), item.properties, str(item.uuid)
        ).__geo_interface__
        for item in starting_points
        if item.geometry is not None
    ]
    agents = generate_agents(starting_points_features, n_agents, steps)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        agents = list(executor.map(move_agent, agents))
        executor.shutdown(wait=True)
        return [a.save_walking_path(store_uuid) for a in agents if a.moved_distance > 0]


def get_sequence_for_sensor(provider_uuid, uuid, start_date, end_date):
    pre_start_date = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(
        hours=168, minutes=0
    )
    sensor_item = ItemDB.find_readable_or_fail(provider_uuid, uuid)
    sid = sensor_item.properties["Cid"]
    df, _ = SensorData.get_data(pre_start_date, end_date)
    end_datetime = pd.to_datetime(df.index.values[-1])
    df = df.loc[df.first_valid_index() : df.last_valid_index()].fillna(0)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../assets/scalers/all_features.joblib")
    x_scaler = joblib.load(path)
    X_scaled = x_scaler.transform(df.values)
    return_df = pd.date_range(
        start_date, end_datetime, freq="H", name="cDte"
    ).to_frame()
    predictions = SensorPrediction.make_prediction(sid, X_scaled, len(return_df))
    return_df["tracked"] = df["s" + str(sid) + "_in"]
    return_df["predicted"] = predictions.astype(int)
    return return_df.rename(columns={"cDte": "datetime"}).to_json(
        orient="split", index=False, date_format="iso"
    )
