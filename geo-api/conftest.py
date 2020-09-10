# module conftest.py
import pytest
from sqlalchemy_utils import database_exists, create_database

from app import create_app
from app import db as _db
from sqlalchemy import event

UUID_ZERO = "00000000-0000-0000-0000-000000000000"


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


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
        print(app.config)
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])
        _db.engine.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        _db.engine.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        _db.drop_all()
        _db.create_all()


@pytest.fixture(scope="session")
def provider(app, db, request):
    from app.models import Provider

    with app.app_context():
        provider = Provider.create(name="test-provider")
        Provider.session().commit()
        return provider.to_dict()


@pytest.fixture(scope="session")
def provider2(app, db, request):
    from app.models import Provider

    with app.app_context():
        provider = Provider.create(name="test-provider2")
        Provider.session().commit()
        return provider.to_dict()


@pytest.fixture(scope="session")
def user(app, db, provider, request):
    from app.models import User

    with app.app_context():
        user = User.create(
            email="test-user@test.se", password="test", provider_uuid=provider["uuid"]
        )
        user.session().commit()
        return user.to_dict()


@pytest.fixture(scope="session")
def user2(app, db, provider2, request):
    from app.models import User

    with app.app_context():
        user = User.create(
            email="test-user2@test.se", password="test", provider_uuid=provider2["uuid"]
        )
        user.session().commit()
        return user.to_dict()


@pytest.fixture(scope="session")
def collection(app, db, provider, request):
    from app.models import Collection

    with app.app_context():
        collection = Collection.create(
            name="test-collection", is_public=True, provider_uuid=provider["uuid"]
        )
        Collection.session().commit()
        return collection.to_dict()


@pytest.fixture(scope="session")
def collection_empty(app, db, provider, request):
    from app.models import Collection

    with app.app_context():
        collection = Collection.create(
            name="test-collection-empty", is_public=True, provider_uuid=provider["uuid"]
        )
        Collection.session().commit()
        return collection.to_dict()


@pytest.fixture(scope="session")
def collection_private(app, db, provider, request):
    from app.models import Collection

    with app.app_context():
        collection = Collection.create(
            name="test-collection-private",
            is_public=False,
            provider_uuid=provider["uuid"],
        )
        Collection.session().commit()
        return collection.to_dict()


@pytest.fixture(scope="session")
def obstacles(app, db, provider, request):
    import json
    import os.path
    from shapely.geometry.geo import shape
    from app.models import Collection, Item

    with app.app_context():
        collection = Collection.create(
            name="obstacles", is_public=True, provider_uuid=provider["uuid"]
        )

        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "data/obstacles.json")
        with open(path) as f:
            data = json.load(f)
            for feature in data["features"]:
                Item.create(
                    collection_uuid=collection.uuid,
                    properties=feature["properties"],
                    geometry=shape(feature["geometry"]).to_wkt(),
                )
        Collection.session().commit()
        return collection.to_dict()


@pytest.fixture(scope="session")
def sensors(app, db, provider, request):
    import json
    import os.path
    from shapely.geometry.geo import shape
    from app.models import Collection, Item

    with app.app_context():
        collection = Collection.create(
            name="sensors", is_public=True, provider_uuid=provider["uuid"]
        )
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "data/sensors.json")
        with open(path) as f:
            data = json.load(f)
            for feature in data["features"]:
                Item.create(
                    collection_uuid=collection.uuid,
                    properties=feature["properties"],
                    geometry=shape(feature["geometry"]).to_wkt(),
                )
        Collection.session().commit()
        return collection.to_dict()


@pytest.fixture(scope="session")
def item(app, db, provider, collection, request):
    from app.models import Item

    with app.app_context():
        item = Item.create(
            collection_uuid=collection["uuid"],
            geometry="POINT(1 1)",
            properties={"name": "test-item"},
        )
        Item.session().commit()
        return item.to_dict()


@pytest.fixture(scope="session")
def item_private(app, db, provider, collection_private, request):
    from app.models import Item

    with app.app_context():
        item = Item.create(
            collection_uuid=collection_private["uuid"],
            geometry="POINT(1 1)",
            properties={"name": "test-item-private"},
        )
        Item.session().commit()
        return item.to_dict()


@pytest.fixture(scope="session")
def item_empty_geom(app, db, provider, collection, request):
    from app.models import Item

    with app.app_context():
        item = Item.create(
            collection_uuid=collection["uuid"],
            geometry=None,
            properties={"name": "test-item-empty"},
        )
        Item.session().commit()
        return item.to_dict()


@pytest.fixture(scope="session")
def client(
    app,
    db,
    provider,
    user,
    provider2,
    user2,
    collection,
    collection_private,
    collection_empty,
    obstacles,
    sensors,
    item,
    item_empty_geom,
    item_private,
    request,
):
    from app.services.session import create_access_token

    provider_uuid = str(provider["uuid"])
    with app.app_context():
        token = create_access_token(user["uuid"], provider_uuid)
    client = app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = "Bearer " + token
    client.environ_base["HTTP_CONTENT_TYPE"] = "application/json"
    client.environ_base["HTTP_ACCEPT"] = "application/json"
    return client


@pytest.fixture(scope="session")
def client2(
    app,
    db,
    provider,
    user,
    provider2,
    user2,
    collection,
    collection_private,
    collection_empty,
    obstacles,
    sensors,
    item,
    item_empty_geom,
    item_private,
    request,
):
    from app.services.session import create_access_token

    provider_uuid = str(provider2["uuid"])
    with app.app_context():
        token = create_access_token(user2["uuid"], provider_uuid)
    client = app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = "Bearer " + token
    client.environ_base["HTTP_CONTENT_TYPE"] = "application/json"
    client.environ_base["HTTP_ACCEPT"] = "application/json"
    return client


@pytest.fixture(scope="session")
def anon_client(
    app,
    db,
    provider,
    user,
    provider2,
    user2,
    collection,
    collection_private,
    collection_empty,
    obstacles,
    sensors,
    item,
    item_empty_geom,
    item_private,
    request,
):
    client = app.test_client()
    client.environ_base["HTTP_CONTENT_TYPE"] = "application/json"
    client.environ_base["HTTP_ACCEPT"] = "application/json"
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

        from app.models import BaseModel

        BaseModel.set_session(sess)

        # establish  a SAVEPOINT just before beginning the test
        # (http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#using-savepoint)
        sess.begin_nested()

        @event.listens_for(sess(), "after_transaction_end")
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
