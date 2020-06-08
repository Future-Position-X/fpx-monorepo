# module conftest.py
import pytest

from app import create_app
from app import db as _db
from sqlalchemy import event


@pytest.fixture(scope="session")
def app(request):
    """
    Returns session-wide application.
    """
    return create_app("testing")

@pytest.fixture(scope="session")
def db(app, request):
    """
    Returns session-wide initialised database.
    """
    with app.app_context():
        _db.drop_all()
        _db.create_all()

@pytest.fixture(scope="session")
def provider(app, db, request):
    """
    Returns session-wide initialised database.
    """
    from app.models import Provider
    with app.app_context():
        provider = Provider.create(name='test-provider')
        Provider.session().commit()
        return provider.to_dict()

@pytest.fixture(scope="session")
def collection(app, provider, request):
    """
    Returns session-wide initialised database.
    """
    from app.models import Collection
    with app.app_context():
        collection = Collection.create(name='test-collection', is_public=True, provider_uuid=provider['uuid'])
        Collection.session().commit()
        return collection.to_dict()

@pytest.fixture(scope="session")
def item(app, provider, collection, request):
    """
    Returns session-wide initialised database.
    """
    from app.models import Item
    with app.app_context():
        item = Item.create(collection_uuid=collection['uuid'], provider_uuid=provider['uuid'], geometry='POINT(1 1)', properties={'name': 'test-item'})
        Item.session().commit()
        return item.to_dict()

@pytest.fixture(scope="session")
def client(app, provider, collection, request):
    from app.services.session import create_access_token
    provider_uuid = str(provider['uuid'])
    with app.app_context():
        token = create_access_token('abc123', provider_uuid)
    client = app.test_client()
    client.environ_base[
        'HTTP_AUTHORIZATION'] = 'Bearer ' + token
    client.environ_base['HTTP_CONTENT_TYPE'] = 'application/json'
    return client



@pytest.fixture(scope="function", autouse=True)
def session(app, db, request):
    """
    Returns function-scoped session.
    """
    with app.app_context():
        conn = _db.engine.connect()
        txn = conn.begin()

        options = dict(bind=conn, binds={})
        sess = _db.create_scoped_session(options=options)

        from app.models import BaseModel2
        BaseModel2.set_session(sess)

        # establish  a SAVEPOINT just before beginning the test
        # (http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#using-savepoint)
        sess.begin_nested()

        @event.listens_for(sess(), 'after_transaction_end')
        def restart_savepoint(sess2, trans):
            # Detecting whether this is indeed the nested transaction of the test
            if trans.nested and not trans._parent.nested:
                # The test should have normally called session.commit(),
                # but to be safe we explicitly expire the session
                sess2.expire_all()
                sess.begin_nested()

        _db.session = sess
        yield sess

        # Cleanup
        sess.remove()
        # This instruction rollsback any commit that were executed in the tests.
        txn.rollback()
        conn.close()