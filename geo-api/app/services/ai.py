import concurrent.futures
import random
import json
from app.services.collection import (
    get_collection_uuid_by_collection_name
)
from app.services.item import get_items_by_collection_uuid_as_geojson
from app.models.ai.walking_agent import WalkingAgent
from app.models.ai.polygon_environment import PolygonEnvironment

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
