from app.stores.base_store import Store
from app.models.collection import Collection


class CollectionStore(Store):
    def insert(self, collection):
        c = self.cursor()
        c.execute("""
            INSERT INTO collections(
                provider_uuid,
                name
            ) VALUES (
                %(provider_uuid)s,
                %(name)s
            )
            RETURNING uuid;
            """, {
            "provider_uuid": collection.provider_uuid,
            "name": collection.name
        })
        return c.fetchone()["uuid"]

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

    def update(self, collection_uuid, collection):
        c = self.cursor()
        c.execute("""
        UPDATE public.collections SET
        name = %(name)s,
        is_public = %(is_public)s
        WHERE uuid = %(collection_uuid)s;
        """, {
            "name": collection.name,
            "is_public": collection.is_public,
            "collection_uuid": collection_uuid
        })