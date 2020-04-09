from app.models.item import Item
from app.services.item import create_item


def test_create_item(mocker):
    # There must be better ways to mock this, problem is magic methods like __enter__
    ItemStoreStub = mocker.MagicMock()
    ItemStoreStub.return_value.__enter__.return_value.insert_one.return_value = "123abc"

    # Be sure to observe that we are mocking the import of ItemStore in app.services.item
    # and not the ItemStore class in app.stores.item
    mocker.patch('app.services.item.ItemStore', new=ItemStoreStub)

    item = Item(**{
        'provider_uuid': '123',
        'collection_uuid': '123',
        'geometry': {},
        'properties': {}
    })
    uuid = create_item(item)

    assert uuid == '123abc'
