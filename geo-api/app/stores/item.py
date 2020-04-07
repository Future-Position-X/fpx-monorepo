from app.stores.base_store import Store, StoreException
from app.models.item import Item

class ItemStore(Store):

    def find_all(self):
        try:
            c = self.cursor()
            c.execute('SELECT uuid, provider_uuid, collection_uuid, properties, ST_AsGeoJSON(geometry) as geometry FROM items LIMIT 100')
            return [Item(**row) for row in c.fetchall()]
        except Exception as e:
            print(e)
            raise StoreException('error finding all items', e)
