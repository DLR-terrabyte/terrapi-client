from typing import Any, Optional
from urllib.parse import urljoin

import pystac
import pystac_client
import requests

from terrabyte_auth.adapter import create_requests_adapter

from .settings import (
    TERRABYTE_PRIVATE_API_URL,
    TERRABYTE_PUBLIC_API_URL,
    TERRABYTE_AUTH_URL,
    TERRABYTE_CLIENT_ID,
)


def open_private_catalog(token: Optional[str] = None) -> pystac_client.Client:
    return pystac_client.Client.open(
        url=TERRABYTE_PRIVATE_API_URL,
        request_modifier=create_requests_adapter(
            TERRABYTE_CLIENT_ID, TERRABYTE_AUTH_URL
        ),
    )


def create_private_collection(
    client: pystac_client.Client, collection: pystac.Collection
):
    client._stac_io.session.post(
        f"{TERRABYTE_PRIVATE_API_URL}/collections", json=collection.to_dict()
    ).raise_for_status()


def update_private_collection(
    client: pystac_client.Client, collection: pystac.Collection
):
    client._stac_io.session.put(
        f"{TERRABYTE_PRIVATE_API_URL}/collections", json=collection.to_dict()
    ).raise_for_status()


def delete_private_collection(
    client: pystac_client.Client, collection: pystac.Collection
):
    client._stac_io.session.delete(
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection.id}"
    ).raise_for_status()


def create_private_item(
    client: pystac_client.Client, item: pystac.Item, collection_id: Optional[str] = None
):
    collection_id = collection_id or item.collection_id
    if not collection_id:
        raise ValueError(f"Could not determine collection ID for item {item}")
    client._stac_io.session.post(
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}", json=item.to_dict()
    ).raise_for_status()


def update_private_item(
    client: pystac_client.Client, item: pystac.Item, collection_id: Optional[str] = None
):
    collection_id = collection_id or item.collection_id
    if not collection_id:
        raise ValueError(f"Could not determine collection ID for item {item}")
    client._stac_io.session.put(
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}/items/{item.id}", json=item.to_dict()
    ).raise_for_status()


def delete_private_item(
    client: pystac_client.Client, item: pystac.Item, collection_id: Optional[str] = None
):
    collection_id = collection_id or item.collection_id
    if not collection_id:
        raise ValueError(f"Could not determine collection ID for item {item}")
    client._stac_io.session.delete(
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}/items/{item.id}"
    ).raise_for_status()


def open_public_catalog() -> pystac_client.Client:
    return pystac_client.Client.open(
        url=TERRABYTE_PUBLIC_API_URL,
    )
