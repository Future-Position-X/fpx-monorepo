from app.stores.base_store import Store, StoreException
from app.models.collection import Collection

class CollectionStore(Store):

    def find_all(self):
        c = self.cursor()
        c.execute('SELECT * FROM collections')
        return [Collection(**row) for row in c.fetchall()]

    def get_uuid_by_name(self, name):
        c = self.cursor()
        c.execute("SELECT uuid FROM collections WHERE name=%(name)s", {'name': name})
        return c.fetchone()['uuid']
