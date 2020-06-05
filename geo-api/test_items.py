import json





def test_test(collection, session):
    from app.models import Item
    Item.set_session(session)
    
    item = Item.create(geometry=None, properties={}, collection_uuid=collection['uuid'], provider_uuid=collection['provider_uuid'])
    #Item.session.commit()
    items=Item.find_by_collection_uuid(collection['uuid'], {'valid': None, 'offset': 0, 'limit': 10, 'property_filter': None})
    print(items[0].to_dict())

    #item2 = items[0]
    #print(item2.provider_uuid)