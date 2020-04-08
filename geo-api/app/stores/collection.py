from app.stores.base_store import Store, StoreException
from app.models.collection import Collection

class CollectionStore(Store):

    def find_all(self):
        try:
            c = self.cursor()
            c.execute('SELECT * FROM collections')
            return [Collection(**row) for row in c.fetchall()]
        except Exception as e:
            print(e)
            raise StoreException('error finding all collections', e)

    def get_uuid_by_name(self, name):
        try:
            c = self.cursor()
            c.execute("SELECT uuid FROM collections WHERE name=%(name)s", {'name': name})
            return c.fetchone()['uuid']
        except Exception as e:
            print(e)
            raise StoreException('error finding named collection', e)
