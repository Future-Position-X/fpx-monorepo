import random
import math
from shapely.geometry import mapping, LineString, shape
from app.dto import ItemDTO
from app.models import Item

class WalkingAgent:
    x = 0
    y = 0
    old_x = 0
    old_y = 0
    startLat = 0
    startLng = 0
    direction = 0
    relative_dir = 0
    speed = 35
    steps = 0
    coordinates_path = []
    started_at_uuid = ""
    coordinates_path = []
    moved_distance = 0
    def __init__(self, starting_point, steps):
        self.direction = random.uniform(0, 2*math.pi)
        self.startLng = starting_point["geometry"]["coordinates"][0]
        self.startLat = starting_point["geometry"]["coordinates"][1]
        self.started_at_uuid = starting_point["id"]
        self.coordinates_path = []
        self.steps = steps
        return

    def __updatePosition(self, env):
        new_x = round(self.x + random.randint(5, self.speed) * math.cos(self.direction))
        new_y = round(self.y + random.randint(5, self.speed) * math.sin(self.direction))
        movement_line = LineString([(self.x,self.y), (new_x,new_y)])
        if not env.check_poly_intersections(movement_line):
            self.old_x = self.x
            self.old_y = self.y
            self.x = new_x
            self.y = new_y
            self.coordinates_path.append([self.x / env.scale, self.y / env.scale])
            self.moved_distance += self.speed
            return True
        else:
            self.direction += random.uniform(-0.2, 0.2)
            self.x = self.old_x
            self.y = self.old_y
            return False

    def path_as_geo_dict(self):
        if len(self.coordinates_path) <= 1:
            return {'type': 'Empty'}
        return {'type': 'Feature', 'properties': {
            "color": "rgba(" + str(random.randrange(150, 255)) + ", " + str(random.randrange(150, 255)) + ", " + str(random.randrange(150, 255)) + ", 150)",
            "starting_point_item_uuid": self.started_at_uuid}, 
            "geometry": mapping(LineString(self.coordinates_path))
        }

    def move(self, env):
        self.x = (self.startLng) * env.scale
        self.y = (self.startLat) * env.scale
        self.old_x = self.x
        self.old_y = self.y
        self.coordinates_path.append([(self.x / env.scale), (self.y / env.scale)])
        for _ in range(self.steps):
            self.relative_dir = random.uniform(-0.2, 0.2)
            self.direction += self.relative_dir
            self.__updatePosition(env)

    def save_walking_path(self, store_collection_uuid):
        item_hash = self.path_as_geo_dict()
        if item_hash["type"] != "Empty":
            item_hash["collection_uuid"] = store_collection_uuid
            item_hash["geometry"] = shape(item_hash['geometry']).to_wkt()
            item = ItemDTO(**item_hash)
            return Item.create(**item.to_dict())
