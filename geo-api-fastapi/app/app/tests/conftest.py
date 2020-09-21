from typing import Dict, Generator
import bcrypt
import pytest
from app.models import BaseModel
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.main import app
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers
from sqlalchemy_utils import database_exists, create_database
from app.db.session import SessionLocal, engine
from sqlalchemy import event


@pytest.fixture(scope="session")
def db() -> Generator:
    if not database_exists(settings.SQLALCHEMY_DATABASE_URI):
        create_database(settings.SQLALCHEMY_DATABASE_URI)
    engine.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    engine.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    BaseModel.metadata.drop_all(bind=engine)
    BaseModel.metadata.create_all(bind=engine)
    _db = SessionLocal()
    BaseModel.set_session(_db)
    yield _db


# @pytest.fixture(scope="module")
# def client() -> Generator:
#     with TestClient(app) as c:
#         yield c
#
#
# @pytest.fixture(scope="module")
# def superuser_token_headers(client: TestClient) -> Dict[str, str]:
#     return get_superuser_token_headers(client)
#
#
# @pytest.fixture(scope="module")
# def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
#     return authentication_token_from_email(
#         client=client, email=settings.EMAIL_TEST_USER, db=db
#     )



UUID_ZERO = "00000000-0000-0000-0000-000000000000"


def hash_pw(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


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
def provider(db, request):
    from app.models import Provider

    provider = Provider.create(name="test-provider1")
    Provider.session.commit()
    return provider.to_dict()


@pytest.fixture(scope="session")
def provider2(db, request):
    from app.models import Provider

    provider = Provider.create(name="test-provider2")
    Provider.session.commit()
    return provider.to_dict()


@pytest.fixture(scope="session")
def user(db, provider, request):
    from app.models import User

    user = User.create(
        email="test-user1@test.se",
        password=hash_pw("test"),
        provider_uuid=provider["uuid"],
    )
    user.session.commit()
    return user.to_dict()


@pytest.fixture(scope="session")
def user2(db, provider2, request):
    from app.models import User

    user = User.create(
        email="test-user2@test.se",
        password=hash_pw("test"),
        provider_uuid=provider2["uuid"],
    )
    user.session.commit()
    return user.to_dict()


@pytest.fixture(scope="session")
def collection(db, provider, request):
    from app.models import Collection

    collection = Collection.create(
        name="test-collection1", is_public=True, provider_uuid=provider["uuid"]
    )
    Collection.session.commit()
    return collection.to_dict()


@pytest.fixture(scope="session")
def collection2(db, provider2, request):
    from app.models import Collection

    collection = Collection.create(
        name="test-collection1", is_public=True, provider_uuid=provider2["uuid"]
    )
    Collection.session.commit()
    return collection.to_dict()


@pytest.fixture(scope="session")
def collection_empty(db, provider, request):
    from app.models import Collection

    collection = Collection.create(
        name="test-collection-empty1",
        is_public=True,
        provider_uuid=provider["uuid"],
    )
    Collection.session.commit()
    return collection.to_dict()


@pytest.fixture(scope="session")
def collection_private(db, provider, request):
    from app.models import Collection

    collection = Collection.create(
        name="test-collection-private1",
        is_public=False,
        provider_uuid=provider["uuid"],
    )
    Collection.session.commit()
    return collection.to_dict()


@pytest.fixture(scope="session")
def obstacles(db, provider, request):
    import json
    import os.path
    from shapely.geometry.geo import shape
    from app.models import Collection, Item

    collection = Collection.create(
        name="obstacles", is_public=True, provider_uuid=provider["uuid"]
    )

    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../../data/obstacles.json")
    with open(path) as f:
        data = json.load(f)
        for feature in data["features"]:
            Item.create(
                collection_uuid=collection.uuid,
                properties=feature["properties"],
                geometry=shape(feature["geometry"]).to_wkt(),
            )
    Collection.session.commit()
    return collection.to_dict()


@pytest.fixture(scope="session")
def sensors(db, provider, request):
    import json
    import os.path
    from shapely.geometry.geo import shape
    from app.models import Collection, Item

    collection = Collection.create(
        name="sensors", is_public=True, provider_uuid=provider["uuid"]
    )
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../../data/sensors.json")
    with open(path) as f:
        data = json.load(f)
        for feature in data["features"]:
            Item.create(
                collection_uuid=collection.uuid,
                properties=feature["properties"],
                geometry=shape(feature["geometry"]).to_wkt(),
            )
    Collection.session.commit()
    return collection.to_dict()


@pytest.fixture(scope="session")
def item(db, provider, collection, request):
    from app.models import Item

    item = Item.create(
        collection_uuid=collection["uuid"],
        geometry="POINT(0 0)",
        properties={"name": "test-item1", "second_prop": "test-prop1"},
    )
    Item.session.commit()
    return item.to_dict()


@pytest.fixture(scope="session")
def item2(db, provider2, collection2, request):
    from app.models import Item

    item = Item.create(
        collection_uuid=collection2["uuid"],
        geometry="POINT(1 1)",
        properties={"name": "test-item2"},
    )
    Item.session.commit()
    return item.to_dict()


@pytest.fixture(scope="session")
def item_poly(db, provider, collection, request):
    from app.models import Item

    item = Item.create(
        collection_uuid=collection["uuid"],
        geometry="POLYGON((0.0 1.0,1.0 1.0,1.0 0.0,0.0 0.0,0.0 1.0))",
        properties={"name": "test-item-poly1"},
    )
    Item.session.commit()
    return item.to_dict()


@pytest.fixture(scope="session")
def item_private(db, provider, collection_private, request):
    from app.models import Item

    item = Item.create(
        collection_uuid=collection_private["uuid"],
        geometry="POINT(1 1)",
        properties={"name": "test-item-private1"},
    )
    Item.session.commit()
    return item.to_dict()


@pytest.fixture(scope="session")
def item_empty_geom(db, provider, collection, request):
    from app.models import Item

    item = Item.create(
        collection_uuid=collection["uuid"],
        geometry=None,
        properties={"name": "test-item-empty1"},
    )
    Item.session.commit()
    return item.to_dict()


@pytest.fixture(scope="session")
def client(
    db,
    provider,
    user,
    provider2,
    user2,
    collection,
    collection2,
    collection_private,
    collection_empty,
    obstacles,
    sensors,
    item,
    item2,
    item_poly,
    item_empty_geom,
    item_private,
    request,
):
    from app.core.security import create_access_token

    provider_uuid = str(provider["uuid"])
    token = create_access_token(user["uuid"])
    with TestClient(app) as client:
        client.headers["AUTHORIZATION"] = "Bearer " + token
        client.headers["HTTP_CONTENT_TYPE"] = "application/json"
        client.headers["HTTP_ACCEPT"] = "application/json"
        return client


@pytest.fixture(scope="session")
def client2(
    db,
    provider,
    user,
    provider2,
    user2,
    collection,
    collection2,
    collection_private,
    collection_empty,
    obstacles,
    sensors,
    item,
    item2,
    item_poly,
    item_empty_geom,
    item_private,
    request,
):
    from app.core.security import create_access_token

    provider_uuid = str(provider2["uuid"])
    token = create_access_token(user2["uuid"])
    with TestClient(app) as client:
        client.headers["HTTP_AUTHORIZATION"] = "Bearer " + token
        client.headers["HTTP_CONTENT_TYPE"] = "application/json"
        client.headers["HTTP_ACCEPT"] = "application/json"
        return client


@pytest.fixture(scope="session")
def anon_client(
    db,
    provider,
    user,
    provider2,
    user2,
    collection,
    collection2,
    collection_private,
    collection_empty,
    obstacles,
    sensors,
    item,
    item2,
    item_poly,
    item_empty_geom,
    item_private,
    request,
):
    with TestClient(app) as client:
        client.headers["HTTP_CONTENT_TYPE"] = "application/json"
        client.headers["HTTP_ACCEPT"] = "application/json"
        return client


@pytest.fixture(scope="function", autouse=True)
def session(db, request):
    """
    Returns function-scoped session.
    """
    # conn = engine.connect()
    # txn = conn.begin()
    #
    # options = dict(bind=conn, binds={})
    # sess = _db.create_scoped_session(options=options)

    sess = db

    from app.models import BaseModel

    BaseModel.set_session(sess)

    # establish  a SAVEPOINT just before beginning the test
    # (http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#using-savepoint)
    sess.begin_nested()

    @event.listens_for(sess, "after_transaction_end")
    def restart_savepoint(sess2, trans):
        # Detecting whether this is indeed the nested transaction of the test
        if trans.nested and not trans._parent.nested:
            # The test should have normally called session.commit(),
            # but to be safe we explicitly expire the session
            sess2.expire_all()
            sess.begin_nested()

    #_db.session = sess
    yield sess

    # Cleanup
    #sess.remove()
    # This instruction rollsback any commit that were executed in the tests.
    #txn.rollback()
    #conn.close()
