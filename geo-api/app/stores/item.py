import rapidjson
from app.stores.base_store import Store
from app.models.item import Item


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

    def insert_one(self, item):
        return self.insert([item])[0]

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

    def find_by_collection_uuid(self, collection_uuid, offset=0, limit=20):
        c = self.cursor()
        c.execute("""
            SELECT uuid,
                provider_uuid,
                collection_uuid,
                properties,
                ST_AsGeoJSON(geometry)::jsonb as geometry
            FROM items
            WHERE collection_uuid = %(collection_uuid)s
                OFFSET %(offset)d
                LIMIT %(limit)d
            """, {
            "collection_uuid": collection_uuid,
            "offset": offset,
            "limit": limit
        })
        return [Item(**row) for row in c.fetchall()]

    def find_by_collection_uuid_as_geojson(self, collection_uuid, offset=0, limit=20):
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
            FROM (
                SELECT *
                FROM public.items
                WHERE collection_uuid = %(collection_uuid)s
                OFFSET %(offset)s
                LIMIT %(limit)s
            )
            inputs) features;
            """, {
            "collection_uuid": collection_uuid,
            "offset": offset,
            "limit": limit
        })
        return c.fetchone()['geojson']
