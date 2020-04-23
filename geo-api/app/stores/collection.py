from app.stores.base_store import Store
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


    def delete(self, collection_uuid):
        c = self.cursor()
        c.execute("""
        DELETE FROM public.items
        WHERE collection_uuid = %(collection_uuid)s;
        DELETE FROM public.collections
        WHERE uuid = %(collection_uuid)s
        """, {'collection_uuid': collection_uuid})