# terrapi-client

The Python library `terrapi-client` offers functions to easily work with the terrabyte User data catalog (STAC API). It builds on top of the Python library `terrapi` (https://github.com/DLR-terrabyte/terrapi) for authentication with the terrabyte authentication service. 

## Installation

```bash
pip install git+https://github.com/DLR-terrabyte/terrapi-client.git
```

## Usage

### Create new private/shared STAC Collection

```python
import pystac
from terrapi.client.stac import open_private_catalog, create_private_collection

# Connect to the terrabyte private STAC API
catalog = open_private_catalog()

# All private collections are prefixed with your terrabyte/LRZ username
# All shared collections are prefixed with the DSS container id (e.g., pn56su-dss-0001)
prefix = '<your username>'

collection = pystac.Collection(
    f"{prefix}.testcollection",
    "description",
    pystac.Extent(
        pystac.SpatialExtent([[-180, -90.180, 90]]),
        pystac.TemporalExtent([[None, None]]),
    ),
)
create_private_collection(catalog, collection)

```

### Create new STAC item in private/shared STAC collection

```python
from terrapi.client.stac import open_private_catalog, create_private_item
from datetime import datetime

# Connect to the terrabyte private STAC API
catalog = open_private_catalog()

# Create STAC item
geom = {"type": "Point", "coordinates": [0, 0]}
item = pystac.Item("test_item", geom, None, datetime=datetime.now(), properties={})

# Add STAC item within STAC collection
create_private_item(catalog, item, collection.id)
```

### Explore the STAC catalog

```python
from terrapi.client.stac import open_private_catalog

# Connect to the terrabyte private STAC API
catalog = open_private_catalog()

# list the IDs of all STAC catalog collections
for collection in catalog.get_all_collections():
    print(collection.id)

# Now query a STAC collection
start = datetime.now().replace(hour=0, minute=0, second=0)
end = datetime.now().replace(hour=23, minute=59, second=59)

query = {
    
}

results = catalog.search(
    collections=[f"{prefix}.testcollection"],
    datetime=[start, end],
    query=query,
)
items = results.item_collection_as_dict()
print("%s items found" % len(items['features']))
```

### Delete STAC item

```python
from terrapi.client.stac import open_private_catalog, delete_private_item

# Connect to the terrabyte private STAC API
catalog = open_private_catalog()

# Delete STAC item within STAC collection
delete_private_item(catalog, item.id, collection.id)
```

### Delete STAC collection

```python
from terrapi.client.stac import open_private_catalog, delete_private_collection

# Connect to the terrabyte private STAC API
catalog = open_private_catalog()

# Delete STAC collection
delete_private_collection(catalog, collection.id)
```
