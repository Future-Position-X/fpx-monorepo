import rapidjson
from app.stores.base_store import Store, StoreException
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

    def find_all(self):
        c = self.cursor()
        c.execute('SELECT uuid, provider_uuid, collection_uuid, properties, ST_AsGeoJSON(geometry) as geometry FROM items LIMIT 100')
        return [Item(**row) for row in c.fetchall()]

    def find_by_collection_uuid(self, collection_uuid):
        c = self.cursor()
        c.execute("""
            SELECT uuid, 
                provider_uuid,
                collection_uuid,
                properties,
                ST_AsGeoJSON(geometry)::jsonb as geometry
            FROM items
            WHERE collection_uuid = %(collection_uuid)s
            LIMIT 100
            """, {"collection_uuid": collection_uuid})
        return [Item(**row) for row in c.fetchall()]
