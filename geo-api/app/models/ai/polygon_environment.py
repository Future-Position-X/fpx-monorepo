from shapely.geometry.polygon import Polygon
from shapely.geometry import shape, LineString


class PolygonEnvironment:
    centerX = 0
    centerY = 0
    scale = 100000
    polygons = []

    def __init__(self, geometries):
        for geometry in geometries:
            self.add_geometry(shape(geometry["geometry"]))

    def check_poly_intersections(self, check_line):
        for line in self.polygons:
            if not check_line.intersection(line).is_empty:
                return True
        return False

    def add_geometry(self, geometry):
        normalized_poly = []
        coords = (
            geometry.exterior.coords if type(geometry) is Polygon else geometry.coords
        )
        for point in coords:
            point = (round(point[0] * self.scale), round(point[1] * self.scale))
            normalized_poly.append(point)
        self.polygons.append(LineString(normalized_poly))
