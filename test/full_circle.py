from datetime import datetime, timedelta
import os
import time

import pystac
import pystac_client

from terrabyte import (
    open_private_catalog,
    open_public_catalog,
)
from terrabyte.client import (
    create_private_collection,
    update_private_collection,
    delete_private_collection,
    create_private_item,
    update_private_item,
    delete_private_item,
)


def get_collection(client: pystac_client.Client, collection_id: str) -> pystac.Collection | None:
    for collection in client.get_collections():
        if collection.id == collection_id:
            return collection
    return None


username = os.environ["TERRABYTE_USERNAME"]
client: pystac_client.Client = open_private_catalog()
timestamp: int = int(time.time())

# create private collection
collection = pystac.Collection(
    f"{username}.{timestamp}",
    "desc",
    pystac.Extent(
        pystac.SpatialExtent([[-180, -90.180, 90]]),
        pystac.TemporalExtent([[None, None]]),
    ),
)
create_private_collection(client, collection)

# assert that collection is here
assert client.get_collection(collection.id)
assert client.get_collection(collection.id).id == collection.id

# update collection
collection_updated = pystac.Collection(
    f"{username}.{timestamp}",
    "new desc",
    pystac.Extent(
        pystac.SpatialExtent([[-180, -90.180, 90]]),
        pystac.TemporalExtent([[None, None]]),
    ),
)
update_private_collection(client, collection_updated)

# assert collection was updated
assert get_collection(client, collection_updated.id).description == collection_updated.description

# create item in collection
geom = {"type": "Point", "coordinates": [0, 0]}
item = pystac.Item("test_item", geom, None, datetime=datetime.now(), properties={})
create_private_item(client, item, collection_updated.id)

# assert item was added
assert get_collection(client, collection_updated.id).get_item(item.id)

# update item in collection
item_updated = pystac.Item("test_item", geom, None, datetime=datetime.now() + timedelta(seconds=5), properties={"newProp": "newValue"})
update_private_item(client, item_updated, collection_updated.id)

# assert that item was updated
# TODO: fix this, maybe caching issue
assert get_collection(client, collection_updated.id).get_item(item_updated.id).properties["newProp"] == item_updated.properties["newProp"]

# delete item
delete_private_item(client, item_updated, collection_updated.id)

# assert item was deleted
assert get_collection(client, collection_updated.id).get_item(item_updated.id) is None

# delete collection
delete_private_collection(client, collection_updated)

# assert collection was deleted
assert get_collection(client, collection_updated.id) is None
