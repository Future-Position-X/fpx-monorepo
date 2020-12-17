from copy import copy
from typing import Dict, Generator

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.core.config import settings
from app.main import app
from app.models.base_model import BaseModel
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers

test_db_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
test_db_session = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)()

async_test_db_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True
)
async_test_db_session = AsyncSession(
    autocommit=False, autoflush=False, bind=async_test_db_engine
)


def override_get_db():
    try:
        session = test_db_session
        with session.no_autoflush as s:
            BaseModel.set_session(s)
    except Exception as e:
        print(e)
        raise e


app.dependency_overrides[get_db] = override_get_db


def get_scalar_result(engine, sql):
    result_proxy = engine.execute(sql)
    result = result_proxy.scalar()
    result_proxy.close()
    engine.dispose()
    return result


def database_exists(url):
    url = copy(make_url(url))
    database = url.database
    url = url.set(database="postgres")
    engine = create_engine(url)
    sql = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
    return get_scalar_result(engine, sql)


def create_database(url):
    url = copy(make_url(url))
    database = url.database
    url = url.set(database="postgres")
    engine = create_engine(url)
    encoding = "utf8"
    template = "template1"
    text = "CREATE DATABASE {0} ENCODING '{1}' TEMPLATE {2}".format(
        database, encoding, template
    )
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    engine.raw_connection().set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    engine.execute(text)


@pytest.fixture(scope="session")
def db() -> Generator:
    print("db")
    if not database_exists(settings.SQLALCHEMY_DATABASE_URI):
        create_database(settings.SQLALCHEMY_DATABASE_URI)
    test_db_engine.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    test_db_engine.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    BaseModel.metadata.drop_all(bind=test_db_engine)
    BaseModel.metadata.create_all(bind=test_db_engine)
    BaseModel.set_session(test_db_session)
    yield test_db_session


# @pytest.fixture(scope="module")
# def client() -> Generator:
#     with TestClient(app) as c:
#         yield c
#
#


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


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
        name="test-collection-empty1", is_public=True, provider_uuid=provider["uuid"]
    )
    Collection.session.commit()
    return collection.to_dict()


@pytest.fixture(scope="session")
def collection_private(db, provider, request):
    from app.models import Collection

    collection = Collection.create(
        name="test-collection-private1", is_public=False, provider_uuid=provider["uuid"]
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
def series(db, item, request):
    from app.models import Series

    series = Series.create(
        item_uuid=item["uuid"],
        data={"name": "test-series1", "second_prop": "test-prop1"},
    )
    Series.session.commit()
    return series.to_dict()


@pytest.fixture(scope="session")
def metric(db, series, request):
    from datetime import datetime

    from app.models import Metric

    metric = Metric.create(
        series_uuid=series["uuid"],
        ts=datetime.fromisoformat("2020-12-01T01:00:00.000"),
        data={"name": "test-series1", "second_prop": "test-prop1", "third_prop": 1},
    )
    Metric.session.commit()
    return metric.to_dict()


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
    series,
    metric,
    request,
):
    from app.core.security import create_access_token

    token = create_access_token(user["uuid"])
    with TestClient(app) as client:
        client.headers["AUTHORIZATION"] = "Bearer " + token
        client.headers["CONTENT_TYPE"] = "application/json"
        client.headers["ACCEPT"] = "application/json"
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
    series,
    metric,
    request,
):
    from app.core.security import create_access_token

    token = create_access_token(user2["uuid"])
    with TestClient(app) as client:
        client.headers["AUTHORIZATION"] = "Bearer " + token
        client.headers["CONTENT_TYPE"] = "application/json"
        client.headers["ACCEPT"] = "application/json"
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
    series,
    metric,
    request,
):
    with TestClient(app) as client:
        client.headers["CONTENT_TYPE"] = "application/json"
        client.headers["ACCEPT"] = "application/json"
        return client


@pytest.fixture(scope="function", autouse=True)
def session(request):
    test_db_session.begin_nested()
    yield test_db_session
    test_db_session.rollback()
    test_db_session.close()
