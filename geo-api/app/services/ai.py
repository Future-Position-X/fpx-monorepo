import concurrent.futures
import random
import json
import joblib
import pandas as pd
from datetime import date, datetime, timedelta
from app.services.collection import (
    get_collection_uuid_by_collection_name
)
from app.services.item import (
    get_item_by_uuid_as_geojson
)

from app.services.item import get_items_by_collection_uuid_as_geojson
from app.models.ai.walking_agent import WalkingAgent
from app.models.ai.polygon_environment import PolygonEnvironment
from app.models.ai.data_preperation.gcs_sensor_data import SensorData
from app.models.ai.data_predictors.sensor_prediction import SensorPrediction

def generate_agents(points, n_agents, pathlength):
    return [WalkingAgent(random.choice(points), pathlength) for a in range(n_agents)]

def move_agent(a):
    global env
    a.move(env)
    return a

def generate_paths_from_points(points_uuid, obstacles_uuid, store_uuid, n_agents, steps, provider_uuid, filters):
    global env
    starting_points = get_items_by_collection_uuid_as_geojson(points_uuid, filters)
    obstacles = get_items_by_collection_uuid_as_geojson(obstacles_uuid, filters)
    env = PolygonEnvironment(obstacles["features"])
    agents = generate_agents(starting_points["features"], n_agents, steps)
    with concurrent.futures.ProcessPoolExecutor() as executor: 
        agents = list(executor.map(move_agent, agents))
        executor.shutdown(wait=True)
        return [a.save_walking_path(provider_uuid, store_uuid) for a in agents if a.moved_distance > 0]

def get_sequence_for_sensor(uuid, filters, start_date, end_date):
    pre_start_date = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(hours=168, minutes=0)
    sensor_item = get_item_by_uuid_as_geojson(uuid)
    sid = sensor_item["properties"]["Cid"]
    df, _ = SensorData.get_data(pre_start_date, end_date)
    end_datetime = pd.to_datetime(df.index.values[-1])
    df = df.loc[df.first_valid_index():df.last_valid_index()].fillna(0)
    x_scaler = joblib.load('app/assets/scalers/all_features.joblib')
    X_scaled = x_scaler.transform(df.values)
    return_df = pd.date_range(start_date, end_datetime, freq='H', name='cDte').to_frame()
    predictions = SensorPrediction.make_prediction(sid, X_scaled, len(return_df))
    return_df['tracked'] = df['s' + str(sid) + '_in']
    return_df['predicted'] = predictions.astype(int)
    return return_df.rename(columns={'cDte': 'datetime'}).to_json(
        orient='split', 
        index=False, 
        date_format='iso'
    )