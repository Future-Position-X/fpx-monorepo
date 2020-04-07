from psycopg2.extras import RealDictCursor
from app.stores.base_store import Store, StoreException
from app.models.collection import Collection
class CollectionStore(Store):

    def find_all(self):
        try:
            c = self.conn.cursor(cursor_factory=RealDictCursor)
            c.execute('SELECT * FROM collections')
            rows = c.fetchall()
            result = []
            for row in rows:
                collection = Collection(**row)
                result.append(collection.as_dict())
            return result
        except Exception as e:
            raise StoreException('error finding all collections', e)
