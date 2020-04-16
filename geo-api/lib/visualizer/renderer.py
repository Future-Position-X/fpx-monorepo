import math
from PIL import Image, ImageDraw, ImagePath
from geo_types import Coords, Bounds, Size
from stitcher import stitch_mapbox_images

TILE_SIZE = 256


def render_feature_collection(fc, width, height, map_id, antialias=6):
    bounds = get_bounds(fc)
    img_size = Size(width, height)
    center = get_center(bounds)
    zoom = calculate_max_zoom(bounds, img_size, center, 1)
    merc_center = transform_to_mercator(center, zoom)
    bg_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    img = Image.new("RGBA", (width * antialias,
                             height * antialias), (0, 0, 0, 0))

    if map_id != "transparent":
        stitch_mapbox_images(bg_img, width, height, center, zoom, map_id)

    draw_ctx = ImageDraw.Draw(img)

    for f in fc["features"]:
        geometry = f["geometry"]
        geo_type = geometry["type"]
        color = get_color(f)

        if geo_type == "Polygon":
            draw_polygon(draw_ctx, antialias, color, geometry["coordinates"],
                         merc_center, zoom, img_size)
        elif geo_type == "LineString":
            draw_linestring(draw_ctx, antialias, color,
                            geometry["coordinates"],
                            merc_center, zoom, img_size)

    img = img.resize((img_size.width, img_size.height), Image.LANCZOS)
    bg_img.paste(img, (0, 0), img)

    return bg_img


def draw_polygon(draw_ctx, antialias, color, polygon, merc_center, zoom,
                 img_size):
    for linestring in polygon:
        draw_linestring(draw_ctx, antialias, color, linestring,
                        merc_center, zoom, img_size)


def draw_linestring(draw_ctx, antialias, color, linestring, merc_center, zoom,
                    img_size):
    vectors = []

    for point in linestring:
        coord = Coords(point[0], point[1])
        merc_point = transform_to_mercator(coord, zoom)
        img_coord = convert_to_img_coords(merc_center, merc_point, img_size, 1)
        vectors.append((img_coord[0] * antialias, img_coord[1] * antialias))

    draw_ctx.line(ImagePath.Path(vectors), color, 10)


def get_color(feature):
    if "color" in feature["properties"]:
        return parse_color(feature["properties"]["color"])

    return (101, 232, 163, int(255 * 0.5))


def parse_color(string):
    tokens = string.replace("rgba(", "").replace(
        ")", "").replace(",", "").split(" ")
    r = int(tokens[0])
    g = int(tokens[1])
    b = int(tokens[2])
    a = int(tokens[3])

    return (r, g, b, a)


def get_center(bounds):
    lng = (bounds.max_x + bounds.min_x) / 2
    lat = (bounds.max_y + bounds.min_y) / 2
    return Coords(lng, lat)


def get_bounds(feature_collection):
    WGS84_LNG_MIN = -180.0
    WGS84_LNG_MAX = 180.0
    WGS84_LAT_MIN = -180.0
    WGS84_LAT_MAX = 180.0

    min_x = WGS84_LNG_MAX
    min_y = WGS84_LAT_MAX
    max_x = WGS84_LNG_MIN
    max_y = WGS84_LAT_MIN

    for coord in enum_coords(feature_collection):
        min_x = min(coord.lng, min_x)
        min_y = min(coord.lat, min_y)
        max_x = max(coord.lng, max_x)
        max_y = max(coord.lat, max_y)

    return Bounds(min_x, min_y, max_x, max_y)


def enum_coords(feature_collection):
    for f in feature_collection["features"]:
        geo_type = f["geometry"]["type"]
        coords = f["geometry"]["coordinates"]

        if geo_type == "Polygon":
            for line_string in coords:
                for point in line_string:
                    yield Coords(point[0], point[1])
        elif geo_type == "LineString":
            for point in coords:
                yield Coords(point[0], point[1])
        elif geo_type == "Point":
            yield Coords(coords[0], coords[1])


def calculate_max_zoom(bounds, img_size, center, stroke_size):
    max_zoom = 20.0

    min = Coords(bounds.min_x, bounds.min_y)
    max = Coords(bounds.max_x, bounds.max_y)
    zoom = max_zoom

    while zoom > 0:
        merc_center = transform_to_mercator(center, zoom)
        merc_min = transform_to_mercator(min, zoom)
        merc_max = transform_to_mercator(max, zoom)
        img_min = convert_to_img_coords(
            merc_center, merc_min, img_size, stroke_size)
        img_max = convert_to_img_coords(
            merc_center, merc_max, img_size, stroke_size)

        minok = (img_min[0] > 0 and img_min[1] > 0 and
                 img_min[0] < img_size.width and img_min[1] < img_size.height)

        maxok = (img_max[0] > 0 and img_max[1] > 0 and
                 img_max[0] < img_size.width and img_max[1] < img_size.height)

        if minok and maxok:
            break

        zoom -= 0.01

    return zoom


def convert_to_img_coords(merc_center, merc_point, img_size, stroke_size):
    scale = 2.0
    x = -1 * (merc_center.lng - merc_point.lng) * scale
    y = -1 * (merc_center.lat - merc_point.lat) * scale
    x = x + img_size.width * 0.5 + stroke_size
    y = y + img_size.height * 0.5 + stroke_size
    return (x, y)


def transform_to_mercator(coords, zoom):
    d2r = math.pi / 180
    size = TILE_SIZE * pow(2, zoom)
    d = size / 2
    bc = size / 360
    cc = size / (2 * math.pi)
    ac = size
    f = min(max(math.sin(d2r * coords.lat), -.9999), .9999)
    x = d + coords.lng * bc
    y = d + .5 * (math.log((1 + f) / (1 - f)) * -cc)

    if x > ac:
        x = ac

    if y > ac:
        y = ac

    return Coords(x, y)
