from app.stores.base_store import Store
from app.models.provider import Provider
from app.stores import session

class ProviderStore(Store):
    @staticmethod
    def insert(provider):
        result = session.execute("""
            INSERT INTO providers(
                name
            ) VALUES (
                :name
            )
            RETURNING uuid;
            """, {
            "name": provider.name
        })
        return result.fetchone()["uuid"]

    def find_all(self):
        c = self.cursor()
        c.execute('SELECT * FROM providers')
        return [Provider(**row) for row in c.fetchall()]

    def get_by_uuid(self, provider_uuid):
        c = self.cursor()
        c.execute("SELECT * FROM providers WHERE uuid = %(uuid)s", {
            "uuid": provider_uuid
        })
        return Provider(**c.fetchall()[0])

    def update(self, provider_uuid, provider):
        c = self.cursor()
        c.execute("""
        UPDATE public.providers SET
        name = %(name)s
        WHERE uuid = %(provider_uuid)s;
        """, {
            "name": provider.name,
            "provider_uuid": provider_uuid
        })
