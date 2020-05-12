import rapidjson
from app.stores.base_store import Store
from app.models.item import Item


def append_property_filter_to_where_clause(where_clause, filter, execute_dict):
    params = filter.split(",")

    for i, p in enumerate(params):
        tokens = p.split("=")
        name = "name_" + str(i)
        value = "value_" + str(i)

        where_clause += " properties->>%(" + \
            name + ")s = %(" + value + ")s"
        execute_dict[name] = tokens[0]
        execute_dict[value] = tokens[1]

        if i < (len(params) - 1):
            where_clause += " AND"

    return where_clause


class ItemStore(Store):
    def insert(self, items):
        c = self.cursor()
        ids = []
        for item in items:
            c.execute("""
                INSERT INTO items(
                    provider_uuid,
                    collection_uuid,
                    properties,
                    geometry
                ) VALUES (
                    %(provider_uuid)s,
                    %(collection_uuid)s,
                    %(properties)s,
                    ST_GeomFromGeoJSON(%(geometry)s)
                )
                RETURNING uuid;
                """, {
                "provider_uuid": item.provider_uuid,
                "collection_uuid": item.collection_uuid,
                "properties": rapidjson.dumps(item.properties),
                "geometry": rapidjson.dumps(item.geometry)
            })
            ids.append(c.fetchone()["uuid"])
        return ids

    def delete(self, item_uuid):
        c = self.cursor()
        c.execute("""
        DELETE
        FROM public.items
        WHERE uuid = %(item_uuid)s
        ;
        """, {"item_uuid": item_uuid})

    def update(self, item_uuid, item):
        c = self.cursor()
        c.execute("""
        UPDATE public.items SET
        geometry = ST_GeomFromGeoJSON(%(geometry)s),
        properties = %(properties)s
        WHERE uuid = %(item_uuid)s;
        """, {
            "geometry": rapidjson.dumps(item.geometry),
            "properties": rapidjson.dumps(item.properties),
            "item_uuid": item_uuid
        })

    def insert_one(self, item):
        return self.insert([item])[0]

    def remove_items_by_collection_uuid(self, provider_uuid, collection_uuid):
        c = self.cursor()
        c.execute("""
        DELETE FROM public.items
        WHERE provider_uuid = %(provider_uuid)s AND collection_uuid = %(collection_uuid)s;
        """, {
            "provider_uuid": provider_uuid,
            "collection_uuid": collection_uuid
        })

    def delete_items(self, collection_uuid):
        c = self.cursor()
        c.execute("""
        DELETE FROM public.items
        WHERE collection_uuid = %(collection_uuid)s;
        """, {"collection_uuid": collection_uuid})

    def find_by_uuid_as_geojson(self, item_uuid):
        c = self.cursor()
        c.execute("""
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', uuid,
                'geometry', ST_AsGeoJSON(geometry)::jsonb,
                'properties', properties
            ) as geojson
            FROM(
                SELECT *
                FROM public.items
                WHERE uuid = %(item_uuid)s
            ) row;
        """, {"item_uuid": item_uuid})
        return c.fetchone()['geojson']

    def find_all(self):
        c = self.cursor()
        c.execute("""
        SELECT uuid,
            provider_uuid,
            collection_uuid,
            properties,
            ST_AsGeoJSON(geometry) as geometry
        FROM items
        LIMIT 100
        """)
        return [Item(**row) for row in c.fetchall()]

    def find_by_collection_uuid(self, collection_uuid, filters):
        c = self.cursor()
        where = "collection_uuid = %(collection_uuid)s"

        if filters["valid"]:
            where += " AND ST_IsValid(geometry)"

        exec_dict = {
            "collection_uuid": collection_uuid,
            "offset": filters["offset"],
            "limit": filters["limit"]
        }

        if filters["property_filter"] is not None:
            where += " AND "
            where = append_property_filter_to_where_clause(
                where, filters["property_filter"], exec_dict)

        c.execute("""
            SELECT uuid,
                provider_uuid,
                collection_uuid,
                properties,
                ST_AsGeoJSON(geometry)::jsonb as geometry
            FROM items
            WHERE """ + where + """
                OFFSET %(offset)s
                LIMIT %(limit)s
            """, exec_dict)
        return [Item(**row) for row in c.fetchall()]

    def find_by_collection_name(self, collection_name, current_provider_uuid, filters):
        c = self.cursor()

        where = """
        collections.name = %(collection_name)s
        AND (
            collections.is_public=true
            OR collections.provider_uuid = %(current_provider_uuid)s
            )"""

        if filters["valid"]:
            where += " AND ST_IsValid(geometry)"

        exec_dict = {
            "collection_name": collection_name,
            "current_provider_uuid": current_provider_uuid,
            "offset": filters["offset"],
            "limit": filters["limit"]
        }

        if filters["property_filter"] is not None:
            where += " AND "
            where = append_property_filter_to_where_clause(
                where, filters["property_filter"], exec_dict)

        c.execute("""
            SELECT items.uuid,
                items.provider_uuid,
                items.collection_uuid,
                items.properties,
                ST_AsGeoJSON(items.geometry)::jsonb as geometry
            FROM items
            LEFT JOIN
                collections on collections.uuid = items.collection_uuid
            WHERE """ + where + """
                OFFSET %(offset)s
                LIMIT %(limit)s
            """, exec_dict)
        return [Item(**row) for row in c.fetchall()]

    def find_by_collection_uuid_as_geojson(self, collection_uuid, filters, transforms):
        c = self.cursor()
        where = "collection_uuid = %(collection_uuid)s"
        transform = "ST_AsGeoJSON(geometry)::jsonb"

        if filters["valid"]:
            where += " AND ST_IsValid(geometry)"

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] == "within-distance":
            where += """
            AND ST_DWithin(
                geometry,
                %(distance.point)s,
                %(distance.d)s,
                False
            )
            """

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] == "intersect":
            where += """
            AND ST_Intersects(
                geometry,
                ST_MakeEnvelope(%(envelope.xmin)s, %(envelope.ymin)s, %(envelope.xmax)s, %(envelope.ymax)s, 4326)
            )
            """

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] == "within":
            where += """
            AND ST_Within(
                geometry,
                ST_MakeEnvelope(%(envelope.xmin)s, %(envelope.ymin)s, %(envelope.xmax)s, %(envelope.ymax)s, 4326)
            )
            """

        exec_dict = {
            "collection_uuid": collection_uuid,
            "offset": filters["offset"],
            "limit": filters["limit"],
        }

        if filters['spatial_filter'] and filters['spatial_filter']['filter'] in ['within', 'intersect']:
            exec_dict.update({
                "envelope.xmin": filters['spatial_filter']['envelope']['xmin'],
                "envelope.ymin": filters['spatial_filter']['envelope']['ymin'],
                "envelope.xmax": filters['spatial_filter']['envelope']['xmax'],
                "envelope.ymax": filters['spatial_filter']['envelope']['ymax'],
            })

        if filters['spatial_filter'] and filters['spatial_filter']['filter'] in ['within-distance']:
            exec_dict.update({
                "distance.point": filters['spatial_filter']['distance']['point'].wkt,
                "distance.d": filters['spatial_filter']['distance']['d'],
            })

        if transforms['simplify'] and transforms['simplify'] > 0.0:
            exec_dict.update({
                "simplify": transforms["simplify"],
            })
            transform = "ST_AsGeoJSON(ST_Simplify(geometry, %(simplify)s, false))::jsonb"

        if filters["property_filter"] is not None:
            where += " AND "
            where = append_property_filter_to_where_clause(
                where, filters["property_filter"], exec_dict)

        c.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(features.feature)) as geojson
            FROM (
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'id', uuid,
                    'geometry', """ + transform + """,
                    'properties', properties
            ) AS feature
            FROM (
                SELECT *
                FROM public.items
                WHERE """ + where + """
                    OFFSET %(offset)s
                    LIMIT %(limit)s
            )
            inputs) features;
            """, exec_dict)
        return c.fetchone()['geojson']

    def find_by_collection_name_as_geojson(self, collection_name, current_provider_uuid, filters):
        c = self.cursor()

        where = """
        collections.name = %(collection_name)s
        AND (
            collections.is_public=true
            OR collections.provider_uuid = %(current_provider_uuid)s
            )"""

        if filters["valid"]:
            where += " AND ST_IsValid(geometry)"

        exec_dict = {
            "collection_name": collection_name,
            "current_provider_uuid": current_provider_uuid,
            "offset": filters["offset"],
            "limit": filters["limit"]
        }

        if filters["property_filter"] is not None:
            where += " AND "
            where = append_property_filter_to_where_clause(
                where, filters["property_filter"], exec_dict)

        c.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(features.feature)) as geojson
            FROM (
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'id', uuid,
                    'geometry', ST_AsGeoJSON(geometry)::jsonb,
                    'properties', properties
            ) AS feature
            FROM (
                SELECT items.uuid,
                items.provider_uuid,
                items.collection_uuid,
                items.properties,
                items.geometry
                FROM items
                LEFT JOIN
                    collections on collections.uuid = items.collection_uuid
                WHERE """ + where + """
                    OFFSET %(offset)s
                    LIMIT %(limit)s
            )
            inputs) features;
            """, exec_dict)
        return c.fetchone()['geojson']

    def find_within_radius_as_geojson(self, filters, point=None, radius=None):
        c = self.cursor()
        c.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(features.feature)) as geojson
            FROM (
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'id', uuid,
                    'geometry', ST_AsGeoJSON(geometry)::jsonb,
                    'properties', properties
                ) AS feature
                FROM (SELECT *
                    FROM public.items
                    WHERE ST_DWithin(
                        geometry,
                        %(point)s,
                        %(radius)s,
                        False
                    )
                    OFFSET %(offset)s
                    LIMIT %(limit)s
                ) inputs
            ) features;
            """, {
            "point": point.wkt,
            "radius": radius,
            "offset": filters["offset"],
            "limit": filters["limit"]
        })
        return c.fetchone()['geojson']
